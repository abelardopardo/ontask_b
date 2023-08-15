"""DB queries to manipulate columns."""
from typing import Dict, List

from django.db import connection
from django.utils.translation import gettext_lazy as _
from psycopg2 import sql

from ontask import OnTaskDBIdentifier

COLUMN_NAME_SIZE = 63

sql_to_ontask_datatype_names = {
    # Translation between SQL data type names, and those handled in OnTask
    'text': 'string',
    'bigint': 'integer',
    'double precision': 'double',
    'boolean': 'boolean',
    'timestamp with time zone': 'datetime',
    'timestamp without time zone': 'datetime'}

ontask_to_sql_datatype_names = {
    # Translation between OnTask data type names and SQL
    dval: key for key, dval in sql_to_ontask_datatype_names.items()
}


def add_column_to_db(
        table_name: str,
        col_name: str,
        col_type: str,
        initial=None,
):
    """Add an extra column of the given type with initial value.

    :param table_name: Table to consider
    :param col_name: Column name
    :param col_type: OnTask column type
    :param initial: initial value
    :return: Nothing. Effect done in the DB
    """
    sql_type = ontask_to_sql_datatype_names[col_type]

    query_skel = 'ALTER TABLE {0} ADD COLUMN {1} ' + sql_type

    query = sql.SQL(query_skel).format(
        sql.Identifier(table_name),
        sql.Identifier(col_name),
        sql.Literal(initial),
    )

    if initial is not None:
        query = query + sql.SQL(' DEFAULT ') + sql.Literal(initial)

    connection.connection.cursor().execute(query)


def copy_column_in_db(
        table_name: str,
        col_from: str,
        col_to: str,
):
    """Copy the values in one column to another.

    :param table_name: Table to process
    :param col_from: Source column
    :param col_to: Destination column
    :return: Nothing. The change is performed in the DB
    """
    query = sql.SQL('UPDATE {0} SET {1}={2}').format(
        sql.Identifier(table_name),
        sql.Identifier(col_to),
        sql.Identifier(col_from),
    )

    connection.connection.cursor().execute(query)


def is_column_in_table(table_name: str, column_name: str) -> bool:
    """Check if a column is in the table.

    :param table_name: Table used for the check
    :param column_name: Column used for the check
    :return: Boolean
    """
    query = sql.SQL(
        'SELECT EXISTS (SELECT 1 FROM information_schema.columns '
        + 'WHERE table_name = {0} AND column_name = {1})',
    ).format(sql.Literal(table_name), sql.Literal(column_name))

    with connection.connection.cursor() as cursor:
        cursor.execute(query, [table_name, column_name])
        return cursor.fetchone()[0]


def is_column_unique(table_name: str, column_name: str) -> bool:
    """Return if a table column has all non-empty unique values.

    :param table_name: table
    :param column_name: column
    :return: Boolean (is unique)
    """
    query = sql.SQL('SELECT COUNT(DISTINCT {0}) = count(*) from {1}').format(
        OnTaskDBIdentifier(column_name),
        sql.Identifier(table_name),
    )

    # Get the result
    with connection.connection.cursor() as cursor:
        cursor.execute(query, [])
        return cursor.fetchone()[0]


def get_df_column_types(table_name: str) -> Dict[str, str]:
    """Get a dictionary of column names and data types in the given table.

    :param table_name: Table name
    :return: Dictionary of column name: SQL Type
    """
    with connection.connection.cursor() as cursor:
        cursor.execute(sql.SQL(
            'SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS '
            + 'WHERE TABLE_NAME = {0}').format(sql.Literal(table_name)))

        type_names = dict(cursor.fetchall())

    return {
        col_name: sql_to_ontask_datatype_names[dtype]
        for col_name, dtype in type_names.items()}


def db_rename_column(table: str, old_name: str, new_name: str):
    """Rename a column in the database.

    :param table: table
    :param old_name: Old name of the column
    :param new_name: New name of the column
    :return: Nothing. Change reflected in the database table
    """
    if len(new_name) > COLUMN_NAME_SIZE:
        raise Exception(
            _('Column name is longer than {0} characters').format(
                COLUMN_NAME_SIZE))

    with connection.connection.cursor() as cursor:
        cursor.execute(sql.SQL('ALTER TABLE {0} RENAME {1} TO {2}').format(
            sql.Identifier(table),
            sql.Identifier(old_name),
            sql.Identifier(new_name),
        ))


def df_drop_column(table_name: str, column_name: str):
    """Drop a column from the DB table storing a data frame.

    :param table_name: Table
    :param column_name: Column name
    :return: Drops the column from the corresponding DB table
    """
    with connection.connection.cursor() as cursor:
        cursor.execute(sql.SQL('ALTER TABLE {0} DROP COLUMN {1}').format(
            sql.Identifier(table_name),
            sql.Identifier(column_name)))


def get_text_column_hash(table_name: str, column_name: str) -> str:
    """Calculate and return the MD5 hash of a text column.

    :param table_name: table to use
    :param column_name: column to pull the values
    :return: MD5 hash of the concatenation of the column values
    """
    query = sql.SQL('SELECT MD5(STRING_AGG({0}, {1})) FROM {2}').format(
        OnTaskDBIdentifier(column_name),
        sql.Literal(''),
        sql.Identifier(table_name),
    )

    with connection.connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]


def get_column_distinct_values(table_name: str, column_name: str) -> List:
    """Extract the values stored in a column of a given table.

    :param table_name: Name of the table
    :param column_name: Name of the column
    :return: List of distinct values
    """
    query = sql.SQL(
        'SELECT DISTINCT {0} FROM {1} WHERE {0} IS NOT NULL').format(
        OnTaskDBIdentifier(column_name),
        sql.Identifier(table_name))

    with connection.connection.cursor() as cursor:
        cursor.execute(query)
        return [item[0] for item in cursor.fetchall()]


def is_unique_column(table_name: str, column_name: str) -> bool:
    """Check if a column has complete, unique non-empty values.

    :param table_name: Name of the table
    :param column_name: Name of the column
    :return: Boolean encoding the answer
    """
    query = sql.SQL(
        'SELECT CASE WHEN COUNT(DISTINCT {0}) = COUNT(*) '
        + 'THEN TRUE ELSE FALSE END FROM {1}').format(
        OnTaskDBIdentifier(column_name),
        sql.Identifier(table_name))

    with connection.connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]
