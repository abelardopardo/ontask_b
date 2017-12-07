# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import logging
import os.path
from collections import OrderedDict
from itertools import izip
import subprocess

import pandas as pd
from django.conf import settings
from django.db import connection
from sqlalchemy import create_engine

from dataops.formula_evaluation import evaluate_node_sql

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

table_prefix = '__ONTASK_WORKFLOW_TABLE_'
df_table_prefix = table_prefix + '{0}'
upload_table_prefix = table_prefix + 'UPLOAD_{0}'

# Query to count the number of rows in a table
query_count_rows = 'SELECT count(*) from "{0}"'

logger = logging.getLogger(__name__)

# Translation between pandas data type names, and those handled in ontask
pandas_datatype_names = {
    'object': 'string',
    'int64': 'integer',
    'float64': 'double',
    'bool': 'boolean',
    'datetime64[ns]': 'datetime'
}

# DB Engine to use with Pandas (required by to_sql, from_sql
engine = None


def create_db_engine():
    """
    Function that creates the engine object to connect to the database. The
    object is required by the pandas functions to_sql and from_sql

    :return: the engine
    """
    # DB engine
    database_url = \
        'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database_name=settings.DATABASES['default']['NAME'],
        )
    engine = create_engine(database_url, echo=False)

    if settings.DEBUG:
        print('Creating engine with ', database_url)

    return engine


def destroy_db_engine(db_engine):
    """
    Method that disposes of the given engine (to guarantee there are no
    connections available
    :param db_engine: Engine to destroy
    :return: Nothing
    """
    db_engine.dispose()


def pg_restore_table(filename):
    """
    Function that given a file produced with a pg_dump, it uploads its
    content to the existing database

    :param filename: File in pg_dump format to restore
    :return:
    """
    process = subprocess.Popen(['psql',
                                '-d',
                                settings.DATABASES['default']['NAME'],
                                '-q',
                                '-f',
                                filename])
    process.wait()


def delete_all_tables():
    """
    Delete all tables related to existing workflows
    :return:
    """

    cursor = connection.cursor()
    table_list = \
        connection.introspection.get_table_list(cursor)
    for tinfo in table_list:
        if not tinfo.name.startswith(table_prefix):
            continue
        cursor.execute('DROP TABLE "{0}";'.format(tinfo.name))

    return

def is_table_in_db(table_name):
    cursor = connection.cursor()
    table_list = \
        connection.introspection.get_table_list(cursor)
    return table_name in [x.name for x in table_list]


def create_table_name(pk):
    """

    :param pk: Primary Key of a workflow
    :return: The unique table name to use to store a workflow data frame
    """
    return df_table_prefix.format(pk)


def create_upload_table_name(pk):
    """

    :param pk: Primary key of a workflow
    :return: The unique table to use to upload a new data frame
    """
    return upload_table_prefix.format(pk)


def load_from_db(pk):
    """
    Load the data frame stored for the workflow with the pk
    :param pk:
    :return: data frame
    """
    return load_table(create_table_name(pk))


def load_table(table_name):
    """

    :param table_name: Table name to read from the db in to data frame
    :return: data_frame or None if it does not exist.
    """
    if table_name not in connection.introspection.table_names():
        return None

    if settings.DEBUG:
        print('Loading table ', table_name)

    return pd.read_sql(table_name, engine)


def store_table(data_frame, table_name):
    """
    Store a data frame in the DB
    :param data_frame: The data frame to store
    :param table_name: The name of the table in the DB
    :return: Nothing. Side effect in the DB
    """

    # We ovewrite the content and do not create an index
    data_frame.to_sql(table_name, engine, if_exists='replace', index=False)

    return


def delete_table(pk):
    """Delete the table representing the workflow with the given PK. Due to
    the dual use of the database, the command has to be executed directly on
    the DB.
    """
    try:
        cursor = connection.cursor()
        cursor.execute('DROP TABLE "{0}";'.format(create_table_name(pk)))
        connection.commit()
    except Exception:
        logger.error(
            'Error while dropping table {0}'.format(create_table_name(pk))
        )


def delete_upload_table(pk):
    """Delete the table used to merge data into the workflow with the given
    PK. Due to the dual use of the database, the command has to be executed
    directly on the DB.
    """
    cursor = connection.cursor()
    cursor.execute('DROP TABLE "{0}"'.format(create_upload_table_name(pk)))
    connection.commit()


def df_column_types_rename(df):
    result = [df[x].dtype.name for x in list(df.columns)]
    for tname, ntname in pandas_datatype_names.items():
        result[:] = [x if x != tname else ntname for x in result]

    return result


def df_drop_column(pk, column_name):
    """
    Drop a column from the DB table storing a data frame
    :param pk: Workflow primary key to obtain table name
    :param column_name: Column name
    :return: Drops the column from the corresponding DB table
    """

    query = 'ALTER TABLE "{0}" DROP COLUMN "{1}"'.format(
        create_table_name(pk),
        column_name
    )
    cursor = connection.cursor()
    cursor.execute(query)


def get_table_data(pk, cond_filter, column_names=None):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param pk: Primary key of the workflow storing the data
    :param cond_filter: Condition object to filter the data (or None)
    :param column_names: optional list of columns to select
    :return: ([list of column names], QuerySet with the data rows)
    """

    # Create the query
    if column_names:
        query = 'SELECT "{0}" from "{1}"'.format(
            '", "'.join(column_names),
            create_table_name(pk)
        )
    else:
        query = 'SELECT * from "{0}"'.format(create_table_name(pk))

    # See if the action has a filter or not
    fields = []
    if cond_filter is not None:
        cond_filter, fields = evaluate_node_sql(cond_filter.formula)
        query += ' WHERE ' + cond_filter

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)

    # Get the data
    return cursor.fetchall()


def execute_select_on_table(pk, fields, values, column_names=None):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param pk: Primary key of the workflow storing the data
    :param fields: List of fields to add to the WHERE clause
    :param values: parameters to match the previous fields
    :param column_names: optional list of columns to select
    :return: ([(list of column names,values)], QuerySet with the data rows)
    """

    # Create the query
    if column_names:
        query = 'SELECT "{0}"'.format(','.join(column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(pk))

    # See if the action has a filter or not
    cursor = connection.cursor()
    if fields:
        query += ' WHERE ' + \
                 ', '.join(['"{0}" = %s'.format(x) for x in fields])
        cursor.execute(query, values)
    else:
        # Execute the query
        cursor.execute(query)

    # Get the data
    return cursor.fetchall()


def get_table_queryset(tablename):
    query = 'SELECT * from "{0}";'.format(tablename)
    try:
        cursor = connection.cursor()
        cursor.execute(query)
    except Exception:
        return None

    return cursor.fetchall()


def query_to_dicts(query_string, *query_args):
    """
    Run a simple query and produce a generator that returns the results as
    a bunch of dictionaries with keys for the column values selected.
    """
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = OrderedDict(izip(col_names, row))
        yield row_dict
    return


def update_row(pk, set_fields, set_values, where_fields, where_values):
    """
    Given a primary key, pairs (set_field, set_value), and pairs (where_field,
    where_value), it updates the row in the table selected with the
    list of (where field = where value) with the values in the assignments in
    the list of (set_fields, set_values)

    :param pk: Primary key to detect workflow
    :param set_fields: List of field names to be updated
    :param set_values: List of values to update the fields of the previous list
    :param where_fields: List of fields used to filter the row in the table
    :param where_values: List of values of the previous fields to filter the row
    :return: The table in the workflow pointed by PK is modified.
    """

    # First part of the query with the table name
    query = 'UPDATE "{0}"'.format(create_table_name(pk))
    # Add the SET field = value clauses
    query += ' SET ' + ', '.join(['"{0}" = %s'.format(x) for x in set_fields])
    # And finally add the WHERE clause
    query += ' WHERE ' + ', '.join(['"{0}" = %s'.format(x)
                                    for x in where_fields])

    # Concatenate the values as parameters to the query
    parameters = set_values + where_values

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, parameters)
    connection.commit()


def get_table_row_by_key(workflow, cond_filter, kv_pair, column_names=None):
    """
    Select the set of elements after filtering and with the key=value pair

    :param workflow: workflow object to get to the table
    :param cond_filter: Condition object to filter the data (or None)
    :param kv_pair: A key=value pair to identify the row. Key is suppose to
           be unique.
    :param column_names: Optional list of column names to select
    :return: A dictionary with the (column_name, value) data or None if the
     row has not been found
    """

    # Create the query
    if column_names:
        query = 'SELECT "{0}"'.format('", "'.join(column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(workflow.id))

    # Create the second part of the query setting key=value
    query += ' WHERE ("{0}" = %s)'.format(kv_pair[0])
    fields = [kv_pair[1]]

    # See if the action has a filter or not
    if cond_filter is not None:
        cond_filter, filter_fields = \
            evaluate_node_sql(cond_filter.formula)
        query += ' AND (' + cond_filter + ')'
        fields = fields + filter_fields

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)

    # Get the data
    qs = cursor.fetchall()

    # If there is anything different than one element, return None
    if len(qs) != 1:
        return None

    # Get the only element
    qs = qs[0]

    # ZIP the values to create a dictionary
    return OrderedDict(zip(workflow.get_column_names(), qs))


def search_table_rows(workflow_id,
                      cv_tuples=None,
                      any_join=True,
                      order_col=None,
                      order_asc=True,
                      column_names=None,
                      pre_filter=None):
    """
    Select rows where for every (column, value) pair, column contains value (
    as in LIKE %value%, these are combined with OR if any is TRUE, or AND if
    any is false, and the result is ordered by the given column and type (if
    given)

    :param workflow_id: workflow object to get to the table
    :param cv_tuples: A column, value, type tuple to search the value in the
    column
    :param any_join: Boolean encoding if values should be combined with OR (or
    AND)
    :param order_col: Order results by this column
    :param order_asc: Order results in ascending values (or descending)
    :param column_names: Optional list of column names to select
    :param pre_filter: Optional filter condition to pre filter the query set.
           the query is built with these terms as requirement AND the cv_tuples.
    :return: The resulting query set
    """

    # Create the query
    if column_names:
        query = 'SELECT "{0}"'.format('", "'.join(column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(workflow_id))

    # Build the query so far appending the filter and/or the cv_tuples
    fields = []
    if pre_filter or cv_tuples:
        query += ' WHERE '

    # Add to the query the suffix derived from the filter
    if pre_filter:
        filter_txt, filter_fields = evaluate_node_sql(pre_filter)
        query += filter_txt
        fields.extend(filter_fields)

    if cv_tuples:
        likes = []
        for name, value, data_type in cv_tuples:
            if data_type == 'string':
                mod_name = '("{0}" LIKE %s)'.format(name)
            else:
                mod_name = '(CAST("{0}" AS TEXT) LIKE %s)'.format(name)

            # Create the second part of the query setting column LIKE '%value%'
            likes.append(mod_name)
            fields.append('%' + value + '%')

        # If there is a pre-filter, the suffix needs to be "AND" with the ones
        # just calculated
        if pre_filter:
            query += ' AND '

        # Combine the search subqueries
        if any_join:
            query += '(' + ' OR '.join(likes) + ')'
        else:
            query += '(' + ' AND '.join(likes) + ')'

    # Add the order if needed
    if order_col:
        query += ' ORDER BY "{0}"'.format(order_col)
    if not order_asc:
        query += ' DESC'

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)

    # Get the data
    return cursor.fetchall()


def delete_table_row_by_key(workflow_id, kv_pair):
    """
    Delete the row in the table attached to a workflow with the given key,
    value pairs

    :param workflow_id: workflow object to get to the table
    :param kv_pair: A key=value pair to identify the row. Key is suppose to
           be unique.
    :return: Drops that row from the table in the DB
    """

    # Create the query
    query = 'DELETE FROM "{0}"'.format(create_table_name(workflow_id))

    # Create the second part of the query setting key=value
    query += ' WHERE ("{0}" = %s)'.format(kv_pair[0])
    fields = [kv_pair[1]]

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)


def num_rows(pk, cond_filter=None):
    """
    Obtain the number of rows of the table storing workflow with given pk
    :param pk: Primary key of the table storing the data frame
    :param cond_filter: Condition element to filter the query
    :return:
    """
    return num_rows_by_name(create_table_name(pk), cond_filter)


def num_rows_by_name(table_name, cond_filter=None):
    """
    Given a table name, get its number of rows
    :param table_name: Table name
    :param cond_filter: Condition element used to filter the query
    :return: integer
    """

    # Initial query with the table name
    query = query_count_rows.format(table_name)

    fields = []
    if cond_filter is not None:
        cond_filter, fields = evaluate_node_sql(cond_filter)
        query += ' WHERE ' + cond_filter

    cursor = connection.cursor()
    cursor.execute(query, fields)
    return cursor.fetchone()[0]


def check_wf_df(workflow):
    """
    Check the consistency between the information stored in the workflow
    and the structure of the underlying dataframe

    :param workflow: Workflow object
    :return: Boolean stating the result of the check. True: Correct.
    """
    # Get the df
    df = load_from_db(workflow.id)

    # Set values in case there is no df
    if df is not None:
        dfnrows = df.shape[0]
        dfncols = df.shape[1]
        df_col_names = list(df.columns)
    else:
        dfnrows = 0
        dfncols = 0
        df_col_names = []

    # Check 1: Number of rows and columns
    if workflow.nrows != dfnrows:
        return False
    if workflow.ncols != dfncols:
        return False

    # Identical sets of columns
    wf_cols = workflow.columns.all()
    if [x.name for x in wf_cols] != df_col_names:
        return False

    # Identical data types
    for n1, n2 in zip(wf_cols, df_col_names):
        if n1.data_type != pandas_datatype_names[df[n2].dtype.name]:
            return False

    return True

