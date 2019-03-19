# -*- coding: utf-8 -*-

import logging
import os.path
import subprocess
import sqlalchemy
from builtins import next
from builtins import zip
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.translation import ugettext as _
from sqlalchemy import create_engine

from dataops.formula_evaluation import NodeEvaluation, evaluate
from ontask import fix_pctg_in_name, OnTaskDataFrameNoKey

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Query to count the number of rows in a table
query_count_rows = 'SELECT count(*) from "{0}"'

logger = logging.getLogger(__name__)


class TypeDict(dict):
    def get(self, key):
        return next(y for x, y in self.items() if key.startswith(x))


# Translation between pandas data type names, and those handled in OnTask
pandas_datatype_names = TypeDict({
    'object': 'string',
    'int64': 'integer',
    'float64': 'double',
    'bool': 'boolean',
    'datetime64[ns': 'datetime'
})

# Translation between SQL data type names, and those handled in OnTask
sql_datatype_names = {
    'text': 'string',
    'bigint': 'integer',
    'double precision': 'double',
    'boolean': 'boolean',
    'timestamp with time zone': 'datetime'
}

# Translation between OnTask data types and SQLAlchemy
ontask_to_sqlalchemy = {
    'string': sqlalchemy.UnicodeText(),
    'integer': sqlalchemy.BigInteger(),
    'double': sqlalchemy.Float(),
    'boolean': sqlalchemy.Boolean(),
    'datetime': sqlalchemy.DateTime(timezone=True)
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

    if settings.DEBUG:
        print('Creating engine with ', database_url)

    return create_engine(database_url,
                         client_encoding=str('utf8'),
                         encoding=str('utf8'),
                         echo=False,
                         paramstyle='format')


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
    the_engine = create_db_connection(dialect,
                                      driver,
                                      username,
                                      password,
                                      host,
                                      dbname)

    return the_engine


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


def is_table_in_db(table_name):
    cursor = connection.cursor()
    return next(
        (True for x in connection.introspection.get_table_list(cursor)
         if x.name == table_name),
        False
    )


def is_column_table_unique(table_name, column_name):
    """
    Given a table_name, see if the given column has unique values
    :param table_name: table
    :param column_name: column
    :return: Boolean (is unique)
    """

    query = 'SELECT COUNT(DISTINCT "{0}") = count(*) from "{1}"'.format(
        fix_pctg_in_name(column_name),
        table_name
    )

    # Get the result
    cursor = connection.cursor()
    cursor.execute(query, [])

    return cursor.fetchone()[0]


def load_from_db(table_name, columns=None, filter_exp=None):
    """
    Load the data frame stored for the workflow with the pk
    :param table_name: Table name
    :param columns: Optional list of columns to load (all if NOne is given)
    :param filter_exp: JSON expression to filter a subset of rows
    :return: data frame
    """
    return load_table(table_name,
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
    :param columns: Optional list of columns to load
    :param filter_exp: Optional filter expression to filter the load
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


def strip_and_convert_to_datetime(data_frame):
    """
    Strip white space from all string columns and try to convert to datetime
    just in case
    :param data_frame:
    :return: new data frame
    """

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


def load_df_from_csvfile(file, skiprows=0, skipfooter=0):
    """
    Given a file object, try to read the content as a CSV file and transform
    into a data frame. The skiprows and skipfooter are number of lines to skip
    from the top and bottom of the file (see read_csv in pandas).

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param file: File object to read the CSV content
    :param skiprows: Number of lines to skip at the top of the document
    :param skipfooter: Number of lines to skip at the bottom of the document
    :return: Resulting data frame, or an Exception.
    """
    data_frame = pd.read_csv(file,
                             index_col=False,
                             infer_datetime_format=True,
                             quotechar='"',
                             skiprows=skiprows,
                             skipfooter=skipfooter,
                             encoding='utf-8')

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return strip_and_convert_to_datetime(data_frame)


def load_df_from_excelfile(file, sheet_name):
    """
    Given a file object, try to read the content as a Excel file and transform
    into a data frame. The sheet_name is the name of the sheet to read.

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param file: File object to read the CSV content
    :param sheet_name: Sheet in the file to read
    :return: Resulting data frame, or an Exception.
    """
    data_frame = pd.read_excel(file,
                               sheet_name=sheet_name,
                               index_col=False,
                               infer_datetime_format=True,
                               quotechar='"')

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return strip_and_convert_to_datetime(data_frame)


def load_df_from_sqlconnection(conn_item, password=None):
    """
    Load a DF from a SQL connection open with the parameters given in conn_item.

    :param conn_item: SQLConnection object with the connection parameters.
    :param password: Password
    :return: Data frame or raise an exception.
    """

    # Get the connection
    db_connection = create_db_connection(conn_item.conn_type,
                                         conn_item.conn_driver,
                                         conn_item.db_user,
                                         password,
                                         conn_item.db_host,
                                         conn_item.db_name)

    # Try to fetch the data
    data_frame = pd.read_sql(conn_item.db_table, db_connection)

    # After reading from the DB, turn all None into NaN
    data_frame.fillna(value=np.nan, inplace=True)

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return strip_and_convert_to_datetime(data_frame)


def load_df_from_googlesheet(url_string, skiprows=0, skipfooter=0):
    """
    Given a file object, try to read the content as a CSV file and transform
    into a data frame. The skiprows and skipfooter are number of lines to skip
    from the top and bottom of the file (see read_csv in pandas).

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param url_string: URL where the file is available
    :param skiprows: Number of lines to skip at the top of the document
    :param skipfooter: Number of lines to skip at the bottom of the document
    :return: Resulting data frame, or an Exception.
    """

    # Process the URL provided by google. If the URL is obtained using the
    # GUI, it has as suffix /edit?[parameters]. This part needs to be
    # replaced by the suffix /export?format=csv
    # For example from:
    # https://docs.google.com/spreadsheets/d/DOCID/edit?usp=sharing
    # to
    # https://docs.google.com/spreadsheets/d/DOCID/export?format = csv&gid=0
    parse_res = urlparse(url_string)
    if parse_res.path.endswith('/edit'):
        url_string = urlunparse([
            parse_res.scheme,
            parse_res.netloc,
            parse_res.path[:-len('/edit')] + '/export',
            parse_res.params,
            parse_res.query + '&format=csv',
            parse_res.fragment
        ])

    # Process the link using pandas read_csv
    return load_df_from_csvfile(url_string, skiprows, skipfooter)


def store_table(data_frame, table_name, dtype=None):
    """
    Store a data frame in the DB. dtype is a dictionary of (column_name,
    column_type) column type can be:

    - 'boolean',
    - 'datetime',
    - 'double',
    - 'integer',
    - 'string'

    The function will use these to translate into (respectively)

    - sqlalchemy.Boolean()
    - sqlalchemy.DateTime()
    - sqlalchemy.Float()
    - sqlalchemy.BigInteger()
    - sqlalchemy.UnicodeText()

    :param data_frame: The data frame to store
    :param table_name: The name of the table in the DB
    :param dtype: dictionary with (column_name, data type) to force the storage
    of certain data types
    :return: Nothing. Side effect in the DB
    """

    if dtype is None:
        dtype = {}

    with cache.lock(table_name):
        # We ovewrite the content and do not create an index
        data_frame.to_sql(
            table_name,
            engine,
            if_exists='replace',
            index=False,
            dtype=dict([(key, ontask_to_sqlalchemy[value])
                        for key, value in dtype.items()])
        )

    return


def delete_table(table_name):
    """Delete the table representing the workflow with the given PK. Due to
    the dual use of the database, the command has to be executed directly on
    the DB.
    :param table_name: Table to delete
    :return: Drop the table in the DB
    """
    try:
        cursor = connection.cursor()
        cursor.execute('DROP TABLE "{0}";'.format(table_name))
        connection.commit()
    except Exception:
        logger.error(
            'Error while dropping table {0}'.format(table_name)
        )


def delete_upload_table(table_name):
    """
    Delete the table used to merge data into the workflow with the given
    PK. Due to the dual use of the database, the command has to be executed
    directly on the DB.
    :param table_name: table to drop
    """
    cursor = connection.cursor()
    cursor.execute('DROP TABLE "{0}"'.format(table_name))
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
    
    :param table_name: Primary key of the workflow containing this data frame
    (table)
    :return: List of data type strings translated to the proper values
    """

    # result = [table_name[x].dtype.name for x in list(table_name.columns)]
    # for tname, ntname in pandas_datatype_names.items():
    #     result[:] = [x if x != tname else ntname for x in result]

    return [sql_datatype_names.get(x) for __, x in
            get_table_column_types(table_name)]


def db_column_rename(table, old_name, new_name):
    """

    :param table: table
    :param old_name: Old name of the column
    :param new_name: New name of the column
    :return: Nothing. Change reflected in the database table
    """
    cursor = connection.cursor()
    query = """ALTER TABLE "{0}" RENAME "{1}" TO "{2}" """.format(
        table,
        old_name,
        new_name
    )
    cursor.execute(query)


def df_drop_column(table_name, column_name):
    """
    Drop a column from the DB table storing a data frame
    :param table_name: Table
    :param column_name: Column name
    :return: Drops the column from the corresponding DB table
    """

    query = 'ALTER TABLE "{0}" DROP COLUMN "{1}"'.format(
        table_name,
        column_name
    )
    cursor = connection.cursor()
    cursor.execute(query)


def get_subframe(table_name, cond_filter, column_names):
    """
    Execute a select query to extract a subset of the dataframe and turn the
     resulting query set into a data frame.
    :param table_name: Table
    :param cond_filter: Condition object to filter the data (or None)
    :param column_names: [list of column names], QuerySet with the data rows
    :return:
    """
    # Get the cursor
    cursor = get_table_cursor(table_name, cond_filter, column_names)

    # Create the DataFrame and set the column names
    result = pd.DataFrame.from_records(cursor.fetchall(), coerce_float=True)
    result.columns = [c.name for c in cursor.description]

    return result


def get_table_cursor(table_name, cond_filter, column_names):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param table_name: Primary key of the workflow storing the data
    :param cond_filter: Condition object to filter the data (or None)
    :param column_names: optional list of columns to select
    :return: ([list of column names], QuerySet with the data rows)
    """

    # Create the query
    safe_column_names = [fix_pctg_in_name(x) for x in column_names]
    query = 'SELECT "{0}" from "{1}"'.format(
        '", "'.join(safe_column_names),
        table_name
    )

    # See if the action has a filter or not
    fields = []
    if cond_filter is not None:
        cond_filter, fields = evaluate(cond_filter.formula,
                                       NodeEvaluation.EVAL_SQL)
        if cond_filter:
            # The condition may be empty, in which case, nothing is needed.
            query += ' WHERE ' + cond_filter

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)

    return cursor


def get_table_data(table_name, cond_filter, column_names):
    # Get first the cursor
    cursor = get_table_cursor(table_name, cond_filter, column_names)

    # Return the data
    return cursor.fetchall()


def execute_select_on_table(table_name, fields, values, column_names):
    """
    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param table_name: Table
    :param fields: List of fields to add to the WHERE clause
    :param values: parameters to match the previous fields
    :param column_names: optional list of columns to select
    :return: QuerySet with the data rows
    """

    # Create the query
    safe_column_names = ['"' + fix_pctg_in_name(x) + '"'
                         for x in column_names]
    query = 'SELECT {0}'.format(','.join(safe_column_names))

    # Add the table
    query += ' FROM "{0}"'.format(table_name)

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
        row_dict = OrderedDict(list(zip(col_names, row)))
        yield row_dict
    return


def update_row(table_name,
               set_fields,
               set_values,
               where_fields,
               where_values):
    """
    Given a primary key, pairs (set_field, set_value), and pairs (where_field,
    where_value), it updates the row in the table selected with the
    list of (where field = where value) with the values in the assignments in
    the list of (set_fields, set_values)

    :param table_name: Table
    :param set_fields: List of field names to be updated
    :param set_values: List of values to update the fields of the previous list
    :param where_fields: List of fields used to filter the row in the table
    :param where_values: List of values of the previous fields to filter the row
    :return: The table in the workflow pointed by PK is modified.
    """

    # First part of the query with the table name
    query = 'UPDATE "{0}"'.format(table_name)
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


def increase_row_integer(table_name, set_field, where_field, where_value):
    """
    Given a primary key, a field set_field, and a pair (where_field,
    where_value), it increases the field in the appropriate row

    :param table_name: Primary key to detect workflow
    :param set_field: name of the field to be increased
    :param where_field: Field used to filter the row in the table
    :param where_value: Value of the previous field to filter the row
    :return: The table in the workflow pointed by PK is modified.
    """

    # First part of the query with the table name
    query = 'UPDATE "{0}" SET "{1}" = "{1}" + 1 WHERE "{2}" = %s'.format(
        table_name,
        set_field,
        where_field
    )

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, [where_value])
    connection.commit()


def get_table_row_by_key(workflow, cond_filter, kv_pair, column_names):
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
    safe_column_names = [fix_pctg_in_name(x) for x in column_names]
    query = 'SELECT "{0}" FROM "{1}" WHERE ("{2}" = %s)'.format(
        '", "'.join(safe_column_names),
        workflow.data_frame_table_name,
        fix_pctg_in_name(kv_pair[0])
    )
    fields = [kv_pair[1]]

    # See if the action has a filter or not
    if cond_filter is not None:
        cond_filter, filter_fields = \
            evaluate(cond_filter.formula, NodeEvaluation.EVAL_SQL)
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
    return OrderedDict(list(zip(workflow.get_column_names(), qs)))


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

    data_type = pandas_datatype_names.get(df_column.dtype.name)

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
    safe_column_names = [fix_pctg_in_name(x) for x in column_names]
    query = 'SELECT "{0}" FROM "{1}"'.format('", "'.join(safe_column_names),
                                             table_name)

    # Calculate the first suffix to add to the query
    filter_txt = ''
    filter_fields = []
    if filter_exp:
        filter_txt, filter_fields = evaluate(filter_exp,
                                             NodeEvaluation.EVAL_SQL)

    # Build the query so far appending the filter and/or the cv_tuples
    if filter_txt:
        query += ' WHERE '

    fields = []
    # If there has been a suffix from the filter, add it.
    if filter_txt:
        query += filter_txt

    if filter_fields:
        fields.extend(filter_fields)

    return query, fields


def search_table_rows(table_name,
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

    :param table_name: table name
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
    safe_column_names = [fix_pctg_in_name(x) for x in column_names]
    query = 'SELECT "{0}" FROM "{1}"'.format('", "'.join(safe_column_names),
                                             table_name)

    # Calculate the first suffix to add to the query
    filter_txt = ''
    filter_fields = []
    if pre_filter:
        filter_txt, filter_fields = evaluate(pre_filter,
                                             NodeEvaluation.EVAL_SQL)

    tuple_txt = ''
    tuple_fields = []
    if cv_tuples:
        likes = []
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


def delete_table_row_by_key(table_name, kv_pair):
    """
    Delete the row in the table attached to a workflow with the given key,
    value pairs

    :param table_name: Table to manipulate
    :param kv_pair: A key=value pair to identify the row. Key is suppose to
    be unique.
    :return: Drops that row from the table in the DB
    """

    # Create the query
    query = 'DELETE FROM "{0}"'.format(table_name)

    # Create the second part of the query setting key=value
    query += ' WHERE ("{0}" = %s)'.format(fix_pctg_in_name(kv_pair[0]))
    fields = [kv_pair[1]]

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query, fields)


def num_rows(table_name, cond_filter=None):
    """
    Obtain the number of rows of the table storing workflow with given pk
    :param table_name: Primary key of the table storing the data frame
    :param cond_filter: Condition element to filter the query
    :return:
    """
    return num_rows_by_name(table_name, cond_filter)


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
        cond_filter, fields = evaluate(cond_filter, NodeEvaluation.EVAL_SQL)
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
    df = load_from_db(workflow.get_data_frame_table_name())

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
    assert workflow.nrows == dfnrows, 'Inconsistent number of rows'

    assert workflow.ncols == dfncols, 'Inconsistent number of columns'

    # Identical sets of columns
    wf_cols = workflow.columns.all()
    assert set([x.name for x in wf_cols]) == set(df_col_names), \
        'Inconsistent set of columns'

    # Identical data types
    # for n1, n2 in zip(wf_cols, df_col_names):
    for col in wf_cols:
        df_dt = pandas_datatype_names.get(df[col.name].dtype.name)
        if col.data_type == 'boolean' and df_dt == 'string':
            # This is the case of a column with Boolean and Nulls
            continue

        assert col.data_type == df_dt, 'Inconsistent data type {0}'.format(
            col.name
        )

    # Verify that the columns marked as unique are preserved
    for col in workflow.columns.filter(is_key=True):
        assert is_unique_column(df[col.name]), \
            'Column {0} should be unique.'.format(col.name)

    return True


def is_unique_column(df_column):
    """

    :param df_column: Column of a pandas data frame
    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.dropna().unique()) == len(df_column)


def are_unique_columns(data_frame):
    """

    :param data_frame: Pandas data frame
    :return: Array of Booleans stating of a column has unique values
    """
    return [is_unique_column(data_frame[x]) for x in list(data_frame.columns)]


def has_unique_column(data_frame):
    """
    Verify if the data frame has a unique column
    :param data_frame:
    :return: Boolean with the result
    """

    return any([is_unique_column(data_frame[x]) for x in data_frame.columns])


def verify_data_frame(data_frame):
    """
    Verify that the data frame complies with two properties:
    1) The names of the columns are all different
    2) There is at least one key column
    :param data_frame: Data frame to verify
    :return: None or an exception with the descripton of the problem in the text
    """

    # If the data frame does not have any unique key, it is not useful (no
    # way to uniquely identify rows). There must be at least one.
    if not has_unique_column(data_frame):
        raise OnTaskDataFrameNoKey(
            _('The data has no column with unique values per row. '
              'At least one column must have unique values.')
        )

    return None
