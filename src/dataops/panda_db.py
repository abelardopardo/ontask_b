# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

import json

from django.conf import settings
from sqlalchemy import create_engine
from django.db import connection
from itertools import izip

from ontask import is_instructor
from workflow.models import Workflow
from action.models import Condition

import pandas as pd

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

table_prefix = '__ONTASK_WORKFLOW_TABLE_{0}'
table_upload_prefix = '__ONTASK_WORKFLOW_TABLE_UPLOAD_{0}'

user = settings.DATABASES['default']['USER']
password = settings.DATABASES['default']['PASSWORD']
database_name = settings.DATABASES['default']['NAME']

database_url = \
    'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
        user=user,
        password=password,
        database_name=database_name,
    )

db_file = 'db.sqlite3'

query_count_rows = 'SELECT count(*) from {0}'

# engine = create_engine(database_url, echo=False)
engine_str = 'sqlite:///' + os.path.join(SITE_ROOT, db_file)
engine = create_engine(engine_str)
if settings.DEBUG:
    print('Creating engine with ', engine_str)

# Cursor to use in the db queries
cursor = connection.cursor()


def is_unique_column(df_column):
    """

    :param df_column: Column of a pandas data frame
    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.unique()) == len(df_column)


def are_unique_columns(data_frame):
    """

    :param data_frame: Pandas data frame
    :return: Array of Booleans stating of a column has unique values
    """
    return [is_unique_column(data_frame[x]) for x in data_frame]


def create_table_name(pk):
    """

    :param pk: Primary Key of a workflow
    :return: The unique table name to use to store a workflow data frame
    """
    return table_prefix.format(pk)


def create_upload_table_name(pk):
    """

    :param pk: Primary key of a workflow
    :return: The unique table to use to upload a new data frame
    """
    return table_upload_prefix.format(pk)


def load_from_table(table_name):
    """

    :param table_name: Table name to read from the db in to data frame
    :return: data_frame or None if it does not exist.
    """
    if settings.DEBUG:
        print('Loading table ', table_name)

    if table_name not in connection.introspection.table_names():
        return None

    return pd.read_sql(table_name, engine)


def load_from_db(pk):
    return load_from_table(create_table_name(pk))


def get_table_data(pk, filter, column_names=None):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param pk: Primary key of the workflow storing the data
    :param filter: Condition object to filter the data (or None)
    :param column_names: optional list of columns to select
    :return: ([list of column names], QuerySet with the data rows)
    """

    # Create the query
    if column_names:
        query = 'SELECT {0} from {1}'.format(
            ','.join(column_names),
            create_table_name(pk)
        )
    else:
        query = 'SELECT * from {0}'.format(create_table_name(pk))

    # See if the action has a filter or not
    if filter is not None:
        filter = evaluate_node(json.loads(filter.formula), None, 'sql')
        query += ' WHERE ' + filter

    # Execute the query
    cursor.execute(query)

    # Get the data
    return cursor.fetchall()


def execute_select_on_table(pk, subquery, fields, column_names=None):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param pk: Primary key of the workflow storing the data
    :param filter: Condition object to filter the data (or None)
    :param column_names: optional list of columns to select
    :return: ([list of column names], QuerySet with the data rows)
    """

    # Create the query
    if column_names:
        query = 'SELECT {0} from {1}'.format(
            ','.join(column_names),
            create_table_name(pk)
        )
    else:
        query = 'SELECT * from {0}'.format(create_table_name(pk))

    # See if the action has a filter or not
    if subquery is not None:
        query += subquery
        cursor.execute(query, fields)
    else:
        # Execute the query
        cursor.execute(query)

    # Get the data
    return cursor.fetchall()


def get_table_column(pk, filter, column_name):
    """
    Given the primary key of a workflow with a table, return the values
    stored in the column with the given name.
    :param pk: Primary key of the workflow
    :param filter: Filter object to filter the query
    :param column_name: column_name
    :return: list of values
    """

    data = get_table_data(pk, filter, [column_name])


def get_table_row(pk, filter, idx):
    """
    Select the set of elements in the row with the given index

    :param pk: Primary key of the workflow storing the data
    :param filter: Condition object to filter the data (or None)
    :param idx: Row number to get (first row is idx = 1)
    :return: A dictionary with the (column_name, value) data or None if the
     index is out of bounds
    """

    # Get the data
    data = get_table_data(pk, filter)

    # If the data is not there, return None
    if idx > len(data):
        return None

    # Get the workflow to get the column names
    workflow = Workflow.objects.get(pk=pk)

    return dict(zip(json.loads(workflow.column_names), data[idx - 1]))


def dump_to_table(data_frame, pk, table_name):
    """
    Update or create a table in the DB with the data in the data frame. It
    also updates the fields column_names, column_types and column_unique

    :param data_frame: Data frame to dump to DB
    :param pk: Corresponding primary key of the workflow
    :param table_name: Table to use in the DB
    :return: Nothing.
    """
    if settings.DEBUG:
        print('Dumping table ', table_name)

    # data_frame.to_sql(table_name, connection, if_exists='replace')
    data_frame.to_sql(table_name, engine, if_exists='replace', index=False)

    # Update the JS structure with the initial operators and names for the
    # columns
    column_names = list(data_frame.columns)
    column_types = df_column_types_rename(data_frame)
    filter_str = []
    for col_name, col_type in zip(column_names, column_types):
        double_valid = ''
        if col_type == 'double':
            # Double field needs validation any to bypass browser forcing
            # integer
            double_valid = ", validation: { step: 'any' }"

        filter_str.append("{{id: '{0}', type: '{1}'{2}}}".format(col_name,
                                                                 col_type,
                                                                 double_valid))
    filter_str = '[{0}]'.format(','.join(filter_str))

    # Update fields and save
    workflow = Workflow.objects.get(pk=pk)
    workflow.nrows = data_frame.shape[0]
    workflow.ncols = data_frame.shape[1]
    workflow.column_names = json.dumps(column_names)
    workflow.column_types = json.dumps(column_types)
    workflow.column_unique = json.dumps(are_unique_columns(data_frame))
    workflow.query_builder_ops = filter_str
    workflow.data_frame_table_name = table_name
    workflow.save()


def dump_to_db(data_frame, pk):
    """
    Given a dataframe and the primary key of a workflow, it dumps its content on
    a table that is rewritten every time.

    :param data_frame: Pandas data frame containing the data
    :param pk: The unique key for the workflow
    :return: Nothing. Side effect in the database
    """
    dump_to_table(data_frame, pk, create_table_name(pk))


def load_upload_from_db(pk):
    return load_from_table(create_upload_table_name(pk))


def dump_upload_to_db(data_frame, pk):
    """
    Given a dataframe and the primary key of a workflow, it dumps its content on
    a table that is rewritten every time.

    :param data_frame: Pandas data frame containing the data
    :param pk: The unique key for the workflow
    :return: Nothing. Side effect in the database
    """
    dump_to_table(data_frame, pk, create_upload_table_name(pk))


def num_rows(pk, filter=None):
    """
    Obtain the number of rows of the table storing workflow with given pk
    :param pk: Primary key of the table storing the data frame
    :return:
    """
    return num_rows_by_name(create_table_name(pk), filter)


def num_rows_by_name(table_name, filter=None):
    """
    Given a table name, get its number of rows
    :param table_name: Table name
    :return: integer
    """

    # Initial query with the table name
    query = query_count_rows.format(table_name)

    if filter is not None:
        filter = evaluate_node(filter, None, 'sql')
        query += ' WHERE ' + filter

    return cursor.execute(query).fetchone()[0]


def perform_dataframe_upload_merge(pk, dst_df, src_df, csv_upload_data):
    """
    It either stores a data frame in the db (dst_df is None), or merges
    the two data frames dst_df and src_df and stores its content.

    :param pk: Primary key of the Workflow containing the data frames
    :param dst_df: Destination dataframe (already stored in DB)
    :param src_df: Source dataframe, stored in temporary table
    :param csv_upload_data: Dictionary with merge options
    :return:
    """

    # STEP 1 Rename the column names.
    src_df = src_df.rename(
        columns=dict(zip(csv_upload_data['initial_column_names'],
                         csv_upload_data.get('autorename_column_names', None) or
                         csv_upload_data['rename_column_names'])))

    # STEP 2 Drop the columns not selected
    columns_to_upload = csv_upload_data['columns_to_upload']
    src_df.drop([n for x, n in enumerate(list(src_df.columns))
                 if not columns_to_upload[x]],
                axis=1, inplace=True)

    # If no dst_df is given, simply dump the frame in the DB
    if dst_df is None:
        dump_to_db(src_df, pk)
        return None

    # Step 3. Drop the columns that are going to be overriden.
    dst_df.drop(csv_upload_data['override_columns_names'],
                inplace=True,
                axis=1)

    # Step 4. Perform the merge
    try:
        new_df = pd.merge(dst_df,
                          src_df,
                          how=csv_upload_data['how_merge'],
                          left_on=csv_upload_data['dst_selected_key'],
                          right_on=csv_upload_data['src_selected_key'])
    except Exception, e:
        return 'Merge operation failed. Exception: ' + e.message

    # Bring the data frame back to the database
    dump_to_db(new_df, pk)

    # Nuke the temporary table
    delete_upload_table(pk)

    return None  # Error message?


def delete_table(pk):
    """Delete the table representing the workflow with the given PK. Due to
    the dual use of the database, the command has to be executed directly on
    the DB.
    """
    cursor.execute("DROP TABLE {0};".format(create_table_name(pk)))
    connection.commit()


def delete_upload_table(pk):
    """Delete the table used to merge data into the workflow with the given
    PK. Due to the dual use of the database, the command has to be executed
    directly on the DB.
    """
    cursor.execute("DROP TABLE {0}".format(create_upload_table_name(pk)))
    connection.commit()


def is_matrix_in_db(table_name):
    table_list = \
        connection.introspection.get_table_list(cursor)
    return table_name in [x.name for x in table_list]


def workflow_has_matrix(workflow_item):
    return is_matrix_in_db(create_table_name(workflow_item.id))


def workflow_id_has_matrix(workflow_id):
    return is_matrix_in_db(create_table_name(workflow_id))


def query_to_dicts(query_string, *query_args):
    """Run a simple query and produce a generator that returns the results as
       a bunch of dictionaries with keys for the column values selected.
    """
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return


def df_column_types_rename(df):
    result = [df[x].dtype.name for x in list(df.columns)]
    result[:] = [x if x != 'object' else 'string' for x in result]
    result[:] = [x if x != 'int64' else 'integer' for x in result]
    result[:] = [x if x != 'float64' else 'double' for x in result]
    result[:] = [x if x != 'bool' else 'boolean' for x in result]

    return result


def workflow_table_info(workflow_id):
    # result to return
    table_info = None

    # Check if the workflow has a table
    if workflow_id_has_matrix(workflow_id):
        # Get the workflow element
        workflow = Workflow.objects.get(id=workflow_id)

        # start populating the result
        table_info = {}

        # Rows and columns
        table_info['num_rows'] = workflow.nrows
        table_info['num_cols'] = workflow.ncols
        # Columns are packed in triplets to be processed by template loop
        table_info['column_info'] = zip(
            json.loads(workflow.column_names),
            json.loads(workflow.column_types),
            json.loads(workflow.column_unique))

    return table_info


def evaluate_top_node(json_str, vars):
    """
    Given a json_string and a dictionary with (varname, varvalue),
    it parses the string and returns the True/False result.
    :param json_str: String produced by jQuery QueryBuilder
    :param vars: Dictionary of (varname, varvalue) for the evaluation
    :return: True/False
    """
    # Translate from JS to Python
    top_node = json.loads(json_str)

    # Pop the "valid" field. It should always be true anyway
    top_node.pop('valid')

    return evaluate_node(top_node, vars)


def evaluate_node(node, given_variables, mode='bool'):
    """
    Given a node representing a query, and a dictionary with (name, values),
    evaluates the expression represented by the node.
    :param node: Node representing the expression
    :param given_variables: Dictionary (name, value) of variables
    :return: True/False depending on the evaluation
    """
    if 'condition' in node:
        # Node is a condition, get the values of the sub-clauses
        sub_clauses = [evaluate_node(x, given_variables, mode)
                       for x in node['rules']]

        # Now combine
        if node['condition'] == 'AND':
            if mode == 'bool':
                result = all(sub_clauses)
            else:
                result = '(' + ') AND ('.join(sub_clauses) + ')'
        else:
            if mode == 'bool':
                result = any(sub_clauses)
            else:
                result = '(' + ') OR ('.join(sub_clauses) + ')'

        if node.pop('not', False):
            if mode == 'bool':
                result = not result
            else:
                result = 'NOT (' + result + ')'

        return result

    # Get the variable name
    varname = node['field']
    # Get the variable value if running in boolean mode
    varvalue = None
    if given_variables is not None:
        varvalue = given_variables.get(varname, None)

    # Get the operator
    operator = node['operator']

    # If calculating a boolean result and no value in the dictionary, finish
    if mode == 'bool' and varvalue is None:
        raise Exception('No value found for variable', varname)

    # If the operator is between or not_between, there is a special case,
    # the constant cannot be computed because the node['value'] is a pair
    constant = None
    if 'between' not in operator:
        # Calculate the constant value depending on the type
        if node['type'] == 'integer':
            constant = int(node['value'])
        elif node['type'] == 'float':
            constant = float(node['value'])
        elif node['type'] == 'string':
            if mode == bool:
                constant = str(node['value'])
            else:
                constant = "'" + node['value'] + "'"
        else:
            raise Exception('No function to translate type', node['type'])

    # Terminal Node
    if operator == 'equal':
        if mode == 'bool':
            result = varvalue == constant
        else:
            result = varname + ' == ' + str(constant)

    elif operator == 'not_equal':
        if mode == 'bool':
            result = varvalue != constant
        else:
            result = varname + '!=' + str(constant)

    # elif operator == 'in':
    #     if mode == 'bool':
    #         result = varvalue in [x for x in constant.split(',')]
    #     else:
    #         # TODO REVIEW
    #         result = varname + " IN (" + \
    #                  ", ".join([x for x in constant.split(',')]) + ")"
    #
    # elif operator == 'not_in':
    #     if mode == 'bool':
    #         result = varvalue not in [x for x in constant.split(',')]
    #     else:
    #         # TODO REVIEW
    #         result = varname + " NOT IN (" + \
    #                  ", ".join([x for x in constant.split(',')]) + ")"

    elif operator == 'begins_with' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue.startswith(constant)
        else:
            result = varname + ' LIKE ' + "'" + node['value'] + "%'"

    elif operator == 'not_begin_with' and node['type'] == 'string':
        if mode == 'bool':
            result = not varvalue.startswith(constant)
        else:
            result = varname + ' NOT LIKE ' + "'" + node['value'] + "%'"

    elif operator == 'contains' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue.find(constant) != -1
        else:
            result = varname + ' LIKE ' + "'%" + node['value'] + "%'"

    elif operator == 'not_contains' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue.find(constant) == -1
        else:
            result = varname + ' NOT LIKE ' + "'%" + node['value'] + "%'"

    elif operator == 'ends_with' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue.endswith(constant)
        else:
            result = varname + ' LIKE ' + "'%" + node['value'] + "'"

    elif operator == 'not_ends_width' and node['type'] == 'string':
        if mode == 'bool':
            result = not varvalue.endswith(constant)
        else:
            result = varname + ' NOT LIKE ' + "'%" + node['value'] + "'"

    elif operator == 'is_empty' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue == ''
        else:
            result = varname + " == ''"

    elif operator == 'is_not_empty' and node['type'] == 'string':
        if mode == 'bool':
            result = varvalue != ''
        else:
            result = varname + " != ''"

    elif operator == 'less' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == 'bool':
            result = varvalue < constant
        else:
            result = varname + ' < ' + str(constant)

    elif operator == 'less_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == 'bool':
            result = varvalue <= constant
        else:
            result = varname + ' <= ' + str(constant)

    elif operator == 'greater' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == 'bool':
            result = varvalue > constant
        else:
            result = varname + ' > ' + str(constant)

    elif operator == 'greater_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == 'bool':
            result = varvalue >= constant
        else:
            result = varname + '>=' + str(constant)

    elif operator == 'between' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == bool:
            result = node['value'][0] <= varvalue <= node['value'][1]
        else:
            result = varname + ' BETWEEN ' + \
                     str(node['value'][0]) + ' AND ' + str(node['value'][1])

    elif operator == 'not_between' and \
            (node['type'] == 'integer' or node['type'] == 'double'):
        if mode == bool:
            result = not (node['value'][0] <= varvalue <= node['value'][1])
        else:
            result = varname + ' NOT BETWEEN ' + \
                     str(node['value'][0]) + ' AND ' + str(node['value'][1])

    else:
        raise Exception('Type, operator, field',
                        node['type'], operator, varname,
                        'not supported yet.')

    if node.get('not', False):
        if mode == 'bool':
            result = not result
        else:
            result = 'NOT (' + result + ')'
        raise Exception('Negation found in unexpected location')

    return result
