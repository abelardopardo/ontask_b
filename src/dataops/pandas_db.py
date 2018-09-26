# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import logging
import os.path
import subprocess
from collections import OrderedDict

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from sqlalchemy import create_engine

from dataops.formula_evaluation import evaluate_node_sql
from ontask import fix_pctg_in_name

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

table_prefix = '__ONTASK_WORKFLOW_TABLE_'
df_table_prefix = table_prefix + '{0}'
upload_table_prefix = table_prefix + 'UPLOAD_{0}'

# Query to count the number of rows in a table
query_count_rows = 'SELECT count(*) from "{0}"'

logger = logging.getLogger(__name__)

# Translation between pandas data type names, and those handled in OnTask
pandas_datatype_names = {
    'object': 'string',
    'int64': 'integer',
    'float64': 'double',
    'bool': 'boolean',
    'datetime64[ns]': 'datetime'
}

# Translation between SQL data type names, and those handled in OnTask
sql_datatype_names = {
    'text': 'string',
    'bigint': 'integer',
    'double precision': 'double',
    'boolean': 'boolean',
    'timestamp without time zone': 'datetime'
}

# DB Engine to use with Pandas (required by to_sql, from_sql
engine = None


def create_db_connection(dialect, driver, username, password, host, dbname):
    """
    Function that creates the engine object to connect to the database. The
    object is required by the pandas functions to_sql and from_sql

    :param dialect: Dialect for the engine (oracle, mysql, postgresql, etc)
    :param driver: DBAPI driver (psycopg2, ...)
    :param username: Username to connect with the database
    :param password: Password to connect with the database
    :param host: Host to connect with the database
    :param dbname: database name
    :return: the engine
    """

    # DB engine
    database_url = \
        '{dialect}{driver}://{user}:{password}@{host}/{database_name}'.format(
            dialect=dialect,
            driver=driver,
            user=username,
            password=password,
            host=host,
            database_name=dbname,
        )
    return create_engine(database_url, echo=False, paramstyle='format')


def create_db_engine(dialect, driver, username, password, host, dbname):
    """
    Function that creates the engine object to connect to the database. The
    object is required by the pandas functions to_sql and from_sql

    :param dialect: Dialect for the engine (oracle, mysql, postgresql, etc)
    :param driver: DBAPI driver (psycopg2, ...)
    :param username: Username to connect with the database
    :param password: Password to connect with the database
    :param host: Host to connect with the database
    :param dbname: database name
    :return: the engine
    """

    # DB engine
    database_url = \
        '{dialect}{driver}://{user}:{password}@{host}/{database_name}'.format(
            dialect=dialect,
            driver=driver,
            user=username,
            password=password,
            host=host,
            database_name=dbname,
        )
    engine = create_db_connection(dialect, driver, username, password, host,
                                  dbname)

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
    table_list = connection.introspection.get_table_list(cursor)
    for tinfo in table_list:
        if not tinfo.name.startswith(table_prefix):
            continue
        cursor.execute('DROP TABLE "{0}";'.format(tinfo.name))

    # To make sure the table is dropped.
    connection.commit()
    return


def is_table_in_db(table_name):
    cursor = connection.cursor()
    return next(
        (True for x in connection.introspection.get_table_list(cursor)
         if x.name == table_name),
        False
    )


def is_wf_table_in_db(workflow):
    return is_table_in_db(create_table_name(workflow.id))


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


def load_from_db(pk, columns=None, filter_exp=None):
    """
    Load the data frame stored for the workflow with the pk
    :param pk: Primary key of the workflow
    :param columns: Optional list of columns to load (all if NOne is given)
    :param filter_exp: JSON expression to filter a subset of rows
    :return: data frame
    """
    return load_table(create_table_name(pk),
                      columns=columns,
                      filter_exp=filter_exp)


def load_table(table_name, columns=None, filter_exp=None):
    """
    Load a data frame from the SQL DB.

    FUTURE WORK:
    Consider to store the dataframes in Redis to reduce load/store time.
    The trick is to use a compressed format:

    SET: redisConn.set("key", df.to_msgpack(compress='zlib'))
    GET: pd.read_msgpack(redisConn.get("key"))

    Need to agree on a sensible item name that does not collide with anything
    else and a policy to detect a cached dataframe and remove it when the data
    changes (difficult to detect? Perhaps df_new.equals(df_current))

    If feasible, a write-through system could be easily implemented.

    :param table_name: Table name to read from the db in to data frame
    :param view: Optional view object to restrict access to the DB
    :return: data_frame or None if it does not exist.
    """
    if table_name not in connection.introspection.table_names():
        return None

    if settings.DEBUG:
        print('Loading table ', table_name)

    if columns or filter_exp:
        # A list of columns or a filter exp is given
        query, params = get_filter_query(table_name, columns, filter_exp)
        result = pd.read_sql_query(query, engine, params=params)
    else:
        # No view given, so simply get the whole table
        result = pd.read_sql(table_name, engine)

    # After reading from the DB, turn all None into NaN
    result.fillna(value=np.nan, inplace=True)
    return result


def load_query(query):
    """
    Load a data frame from the SQL DB running the given query.

    :param query: Query to run in the DB
    :return: data_frame or None if it does not exist.
    """

    if settings.DEBUG:
        print('Loading query ', query)

    result = pd.read_sql_query(query, engine)

    # After reading from the DB, turn all None into NaN
    result.fillna(value=np.nan, inplace=True)
    return result


def load_df_from_csvfile(file, skiprows=0, skipfooter=0):
    """
    Given a file object, try to read the content as a CSV file and transform
    into a data frame. The skiprows and skipfooter are number of lines to skip
    from the top and bottom of the file (see read_csv in pandas).

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param filename: File object to read the CSV content
    :param skiprows: Number of lines to skip at the top of the document
    :param skipfooter: Number of lines to skip at the bottom of the document
    :return: Resulting data frame, or an Exception.
    """
    data_frame = pd.read_csv(
        file,
        index_col=False,
        infer_datetime_format=True,
        quotechar='"',
        skiprows=skiprows,
        skipfooter=skipfooter
    )

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    for x in list(data_frame.columns):
        if data_frame[x].dtype.name == 'object':
            # Column is a string! Remove the leading and trailing white
            # space
            data_frame[x] = data_frame[x].str.strip().fillna(data_frame[x])

            # Try the datetime conversion
            try:
                series = pd.to_datetime(data_frame[x],
                                        infer_datetime_format=True)
                # Datetime conversion worked! Update the data_frame
                data_frame[x] = series
            except (ValueError, TypeError):
                pass
    return data_frame


def load_df_from_sqlconnection(conn_item, pwd=None):
    """
    Load a DF from a SQL connection open with the parameters given in conn_item.

    :param conn_item: SQLConnection object with the connection parameters.
    :return: Data frame or raise an exception.
    """

    # Get the connection
    db_connection = create_db_connection(conn_item.conn_type,
                                         conn_item.conn_driver,
                                         conn_item.db_user,
                                         pwd,
                                         conn_item.db_host,
                                         conn_item.db_name)

    # Try to fetch the data
    result = pd.read_sql(conn_item.db_table, db_connection)

    # After reading from the DB, turn all None into NaN
    result.fillna(value=np.nan, inplace=True)
    return result


def store_table(data_frame, table_name):
    """
    Store a data frame in the DB
    :param data_frame: The data frame to store
    :param table_name: The name of the table in the DB
    :return: Nothing. Side effect in the DB
    """

    with cache.lock(table_name):
        # We ovewrite the content and do not create an index
        data_frame.to_sql(table_name,
                          engine,
                          if_exists='replace',
                          index=False)

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


def get_table_column_types(table_name):
    """
    :param table_name: Table name
    :return: List of pairs (column name, SQL type)
    """
    cursor = connection.cursor()
    cursor.execute("""select column_name, data_type from 
    INFORMATION_SCHEMA.COLUMNS where table_name = '{0}'""".format(table_name))

    return cursor.fetchall()


def df_column_types_rename(table_name):
    """
    
    :param table_name: Primary key of the workflow containing this data frame (table) 
    :return: List of data type strings translated to the proper values
    """
    column_types = get_table_column_types(table_name)

    # result = [table_name[x].dtype.name for x in list(table_name.columns)]
    # for tname, ntname in pandas_datatype_names.items():
    #     result[:] = [x if x != tname else ntname for x in result]

    return [sql_datatype_names[x] for __, x in
            get_table_column_types(table_name)]


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


def get_subframe(pk, cond_filter, column_names=None):
    """
    Execute a select query to extract a subset of the dataframe and turn the
     resulting query set into a data frame.
    :param pk: Workflow primary key
    :param cond_filter: Condition object to filter the data (or None)
    :param column_names: [list of column names], QuerySet with the data rows
    :return:
    """
    # Get the cursor
    cursor = get_table_cursor(pk, cond_filter, column_names)

    # Create the DataFrame and set the column names
    result = pd.DataFrame.from_records(cursor.fetchall(), coerce_float=True)
    result.columns = [c.name for c in cursor.description]

    return result


def get_table_cursor(pk, cond_filter, column_names=None):
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
        safe_column_names = [fix_pctg_in_name(x) for x in column_names]
        query = 'SELECT "{0}" from "{1}"'.format(
            '", "'.join(safe_column_names),
            create_table_name(pk)
        )
    else:
        query = 'SELECT * from "{0}"'.format(create_table_name(pk))

    # See if the action has a filter or not
    fields = []
    if cond_filter is not None:
        cond_filter, fields = evaluate_node_sql(cond_filter.formula)
        if cond_filter:
            # The condition may be empty, in which case, nothing is needed.
            query += ' WHERE ' + cond_filter

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)

    return cursor


def get_table_data(pk, cond_filter, column_names=None):
    # Get first the cursor
    cursor = get_table_cursor(pk, cond_filter, column_names)

    # Return the data
    return cursor.fetchall()


def execute_select_on_table(pk, fields, values, column_names=None):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param pk: Primary key of the workflow storing the data
    :param fields: List of fields to add to the WHERE clause
    :param values: parameters to match the previous fields
    :param column_names: optional list of columns to select
    :return: QuerySet with the data rows
    """

    # Create the query
    if column_names:
        safe_column_names = ['"' + fix_pctg_in_name(x) + '"'
                             for x in column_names]
        query = 'SELECT {0}'.format(','.join(safe_column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(pk))

    # See if the action has a filter or not
    cursor = connection.cursor()
    if fields:
        query += ' WHERE ' + \
                 ' AND '.join(['"{0}" = %s'.format(fix_pctg_in_name(x))
                               for x in fields])
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
        row_dict = OrderedDict(zip(col_names, row))
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
    query += ' SET ' + ', '.join(['"{0}" = %s'.format(fix_pctg_in_name(x))
                                  for x in set_fields])
    # And finally add the WHERE clause
    query += ' WHERE ' + ' AND '.join(['"{0}" = %s'.format(fix_pctg_in_name(x))
                                       for x in where_fields])

    # Concatenate the values as parameters to the query
    parameters = set_values + where_values

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, parameters)
    connection.commit()


def increase_row_integer(pk, set_field, where_field, where_value):
    """
    Given a primary key, a field set_field, and a pair (where_field,
    where_value), it increases the field in the appropriate row

    :param pk: Primary key to detect workflow
    :param set_field: name of the field to be increased
    :param where_field: Field used to filter the row in the table
    :param where_value: Value of the previous field to filter the row
    :return: The table in the workflow pointed by PK is modified.
    """

    # First part of the query with the table name
    query = 'UPDATE "{0}" SET "{1}" = "{1}" + 1 WHERE "{2}" = %s'.format(
        create_table_name(pk),
        set_field,
        where_field
    )

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, [where_value])
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
        safe_column_names = [fix_pctg_in_name(x) for x in column_names]
        query = 'SELECT "{0}"'.format('", "'.join(safe_column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(workflow.id))

    # Create the second part of the query setting key=value
    query += ' WHERE ("{0}" = %s)'.format(fix_pctg_in_name(kv_pair[0]))
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


def get_column_stats_from_df(df_column):
    """
    Given a data frame with a single column, return a set of statistics
    depending on its type.

    :param df_column: data frame with a single column
    :return: A dictionary with keys depending on the type of column
      {'min': minimum value (integer, double an datetime),
       'q1': Q1 value (0.25) (integer, double),
       'mean': mean value (integer, double),
       'median': median value (integer, double),
       'mean': mean value (integer, double),
       'q3': Q3 value (0.75) (integer, double),
       'max': maximum value (integer, double an datetime),
       'std': standard deviation (integer, double),
       'counts': (integer, double, string, datetime, Boolean',
       'mode': (integer, double, string, datetime, Boolean,

       or None if the column has all its values to NaN
    """

    if len(df_column.loc[df_column.notnull()]) == 0:
        # The column has no data
        return None

    # Dictionary to return
    result = {
        'min': 0,
        'q1': 0,
        'mean': 0,
        'median': 0,
        'q3': 0,
        'max': 0,
        'std': 0,
        'mode': None,
        'counts': {},
    }

    data_type = pandas_datatype_names[df_column.dtype.name]

    if data_type == 'integer' or data_type == 'double':
        quantiles = df_column.quantile([0, .25, .5, .75, 1])
        result['min'] = '{0:g}'.format(quantiles[0])
        result['q1'] = '{0:g}'.format(quantiles[.25])
        result['mean'] = '{0:g}'.format(df_column.mean())
        result['median'] = '{0:g}'.format(quantiles[.5])
        result['q3'] = '{0:g}'.format(quantiles[.75])
        result['max'] = '{0:g}'.format(quantiles[1])
        result['std'] = '{0:g}'.format(df_column.std())

    result['counts'] = df_column.value_counts().to_dict()
    mode = df_column.mode()
    if len(mode) == 0:
        mode = '--'
    result['mode'] = mode[0]

    return result


def get_filter_query(table_name, column_names, filter_exp):
    """

    Given a set of columns and a filter expression, return a pair of SQL query
    and params to be executed
    :param table_name: Table to query
    :param column_names: list of columns to consider or None to consider all
    :param filter_exp: Text filter expression
    :return: (sql query, sql params)
    """

    # Create the query
    if column_names:
        safe_column_names = [fix_pctg_in_name(x) for x in column_names]
        query = 'SELECT "{0}"'.format('", "'.join(safe_column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(table_name)

    # Calculate the first suffix to add to the query
    filter_txt = ''
    filter_fields = []
    if filter_exp:
        filter_txt, filter_fields = evaluate_node_sql(filter_exp)

    # Build the query so far appending the filter and/or the cv_tuples
    if filter_txt:
        query += ' WHERE '

    fields = []
    # If there has been a suffix from the filter, add it.
    if filter_txt:
        query += filter_txt

    if filter_fields:
        fields.extend(filter_fields)

    return (query, fields)


def search_table_rows(workflow_id,
                      cv_tuples=None,
                      any_join=True,
                      order_col_name=None,
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
    :param order_col_name: Order results by this column
    :param order_asc: Order results in ascending values (or descending)
    :param column_names: Optional list of column names to select
    :param pre_filter: Optional filter condition to pre filter the query set.
           the query is built with these terms as requirement AND the cv_tuples.
    :return: The resulting query set
    """

    # Create the query
    if column_names:
        safe_column_names = [fix_pctg_in_name(x) for x in column_names]
        query = 'SELECT "{0}"'.format('", "'.join(safe_column_names))
    else:
        query = 'SELECT *'

    # Add the table
    query += ' FROM "{0}"'.format(create_table_name(workflow_id))

    # Calculate the first suffix to add to the query
    filter_txt = ''
    filter_fields = []
    if pre_filter:
        filter_txt, filter_fields = evaluate_node_sql(pre_filter)

    if cv_tuples:
        likes = []
        tuple_fields = []
        for name, value, data_type in cv_tuples:
            # Make sure we escape the name and search as text
            name = fix_pctg_in_name(name)
            mod_name = '(CAST("{0}" AS TEXT) LIKE %s)'.format(name)

            # Create the second part of the query setting column LIKE '%value%'
            likes.append(mod_name)
            tuple_fields.append('%' + value + '%')

        # Combine the search subqueries
        if any_join:
            tuple_txt = '(' + ' OR '.join(likes) + ')'
        else:
            tuple_txt = '(' + ' AND '.join(likes) + ')'

    # Build the query so far appending the filter and/or the cv_tuples
    if filter_txt or cv_tuples:
        query += ' WHERE '

    fields = []
    # If there has been a suffix from the filter, add it.
    if filter_txt:
        query += filter_txt
        fields.extend(filter_fields)

    # If there is a pre-filter, the suffix needs to be "AND" with the ones
    # just calculated
    if filter_txt and cv_tuples:
        query += ' AND '

    if cv_tuples:
        query += tuple_txt
        fields.extend(tuple_fields)

    # Add the order if needed
    if order_col_name:
        query += ' ORDER BY "{0}"'.format(fix_pctg_in_name(order_col_name))
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
    query += ' WHERE ("{0}" = %s)'.format(fix_pctg_in_name(kv_pair[0]))
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
        df_dt = pandas_datatype_names[df[n2].dtype.name]
        if n1.data_type == 'boolean' and df_dt == 'string':
            # This is the case of a column with Boolean and Nulls
            continue

        if n1.data_type != df_dt:
            return False

    return True
