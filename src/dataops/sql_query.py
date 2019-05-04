# -*- coding: utf-8 -*-

"""Direct SQL operations in the DB."""

import logging
from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.db import connection
from psycopg2 import sql
from psycopg2.extras import DictCursor

from dataops.formula_evaluation import NodeEvaluation, evaluate_formula

logger = logging.getLogger('ontask')

# Translation between SQL data type names, and those handled in OnTask
sql_to_ontask_datatype_names = {
    'text': 'string',
    'bigint': 'integer',
    'double precision': 'double',
    'boolean': 'boolean',
    'timestamp with time zone': 'datetime',
}

# Translation between OnTask data type names and SQL
ontask_to_sql_datatype_names = {
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

    :return:
    """
    sql_type = ontask_to_sql_datatype_names[col_type]

    query_skel = 'ALTER TABLE {0} ADD COLUMN {1} ' + sql_type

    query = sql.SQL(query_skel).format(
        sql.Identifier(table_name),
        sql.Identifier(col_name),
        sql.Literal(initial),
    )

    if initial:
        query = sql.SQL(' DEFAULT ').join([query, sql.Literal(initial)])

    connection.cursor().execute(query)


def get_boolean_clause(
    filter_formula: Optional[Dict] = None,
    filter_pairs: Optional[Mapping] = None,
    conjunction: bool = True,
):
    """Create the boolean clause based on a formula and a list of pairs.

    Create the SQL boolean clause to be added to a query by combining a
    formula and a dictionary with key:value pairs. Both of them are optional
    and are combined through conjunction/disjunction depending on the
    conjunction variable.

    :param filter_formula: Boolean formula

    :param filter_pairs: Dictionary of key/value pairs.

    :return: SQL clause
    """
    clause = None
    clause_fields = []

    if filter_formula:
        # There is a filter
        clause, clause_fields = evaluate_formula(
            filter_formula,
            NodeEvaluation.EVAL_SQL,
        )

    if filter_pairs:
        c_txt = ' AND ' if conjunction else ' OR '
        pairs_clause = sql.SQL(c_txt).join([
            sql.SQL('{0} = {1}').format(
                sql.Identifier(key), sql.Literal(lit_val))
            for key, lit_val in filter_pairs
        ])
        pairs_fields = [lit_val for __, lit_val in filter_pairs]
        if clause:
            clause = sql.SQL(' AND ').join([clause, pairs_clause])
            clause_fields += pairs_fields
        else:
            clause = pairs_clause
            clause_fields = pairs_fields

    return clause, clause_fields


def get_select_query(
    table_name: str,
    column_names: Optional[List[str]] = None,
    filter_formula: Optional[Dict] = None,
    filter_pairs: Optional[Mapping] = None,
) -> Tuple[sql.Composed, List[Any]]:
    """Calculate pair query, fields to execute a select statement.

    :param table_name: Table to query

    :param column_names: list of columns to consider or None to consider all

    :param filter_formula: Text filter expression

    :param filter_pairs: Dictionary of key/value pairs.

    :return: (sql query, sql params)
    """
    if not column_names:
        column_names = ['*']

    query = sql.SQL('SELECT {0} FROM {1}').format(
        sql.SQL(', ').join([
            sql.Identifier(cname) for cname in column_names
        ]),
        sql.Identifier(table_name),
    )
    query_fields = []

    if filter_formula or filter_pairs:
        bool_clause, query_fields = get_boolean_clause(
            filter_formula=filter_formula,
            filter_pairs=filter_pairs,
        )

        query = sql.SQL(' WHERE ').join([query, bool_clause])

    return query, query_fields


def get_select_query_txt(
    table_name: str,
    column_names: Optional[List[str]] = None,
    filter_formula: Optional[Dict] = None,
    filter_pairs: Optional[Mapping] = None,
) -> Tuple[str, List[Any]]:
    """Calculate the text representation of a query to select table subset.

    :param table_name: Table to query

    :param column_names: list of columns to consider or None to consider all

    :param filter_formula: Text filter expression

    :param filter_pairs: Dictionary of key/value pairs.

    :return: (sql query, sql params)
    """
    # invoke get_select_query and transform into string
    query_str, fields = get_select_query(
        table_name,
        column_names=column_names,
        filter_formula=filter_formula,
        filter_pairs=filter_pairs,
    )

    return query_str.as_string(connection.connection), fields


def get_rows(
    table_name: str,
    column_names: Optional[List[str]] = None,
    filter_formula: Optional[Mapping] = None,
    filter_pairs: Optional[Mapping] = None,
):
    """Get columns in a row selected by filter and/or pairs.

    Execute a select query in the database with an optional filter and
    pairs and return a subset of columns (or all of them if empty)

    :param table_name: Primary key of the workflow storing the data

    :param column_names: optional list of columns to select

    :param filter_formula: Optional JSON formula to use in the WHERE clause

    :param filter_pairs: Pairs key: value to filter in the WHERE clause

    :return: cursor resulting from the query
    """
    query, fields = get_select_query(
        table_name,
        column_names=column_names,
        filter_formula=filter_formula,
        filter_pairs=filter_pairs,
    )

    # Execute the query
    cursor = connection.connection.cursor(cursor_factory=DictCursor)
    cursor.execute(query, fields)
    return cursor


def get_row(
    table_name: str,
    key_name: str,
    key_value,
    column_names: Optional[List[str]] = None,
    filter_formula: Optional[Mapping] = None,
    filter_pairs: Optional[Mapping] = None,
):
    """Get a single row in the DB with the key name/value pair.

    :param table_name: Name of the table

    :param key_name: Key name to uniquely identify the row

    :param key_value: Key value to uniquely identify the row

    :param column_names: Columns to access (all of them if empty)

    :param filter_formula: Optional filter formula

    :param filter_pairs: Optional dictionary to restrict the clause

    :return: Dictionary with the row
    """
    key_pair = {key_name: key_value}
    if filter_pairs:
        filter_pairs = dict(key_pair, **filter_pairs)
    else:
        filter_pairs = key_pair

    query, fields = get_select_query(
        table_name,
        column_names=column_names,
        filter_formula=filter_formula,
        filter_pairs=filter_pairs,
    )

    # Execute the query
    cursor = connection.connection.cursor(cursor_factory=DictCursor)
    cursor.execute(query, fields)

    if cursor.rowcount != 1:
        raise Exception('Query returned more than one row.')

    return cursor.fetchone()


def update_row(
    table_name: str,
    set_pairs: Mapping,
    filter_pairs: Optional[Mapping] = None,
):
    """Update table row with a set of pairs where determined by filter pairs.

    Given a table, a list of  (set_field, set_value), and pairs (where_field,
    where_value), it updates the row in the table selected with the list of (
    where field = where value) with the values in the assignments in the list
    of (set_fields, set_values)

    :param table_name: Table name

    :param set_fields: List of field names to be updated

    :param set_values: List of values to update the fields of the previous list

    :param where_fields: List of fields used to filter the row in the table

    :param where_values: List of values of the previous fields to filter the
    row

    :return:
    """
    query = sql.SQL(' ').join([
        sql.SQL('UPDATE {0} SET ').format(sql.Identifier(table_name)),
        sql.SQL(' AND ').join([
            sql.SQL('{0} = {1}').format(
                sql.Identifier(key), sql.Literal(lit_val))
            for key, lit_val in set_pairs
        ]),
    ])
    query_fields = []

    if filter_pairs:
        query = sql.SQL(' WHERE ').join([
            query,
            sql.SQL(' AND ').join([
                sql.SQL('{0} = {1}').format(
                    sql.Identifier(key), sql.Literal(lit_val))
                for key, lit_val in filter_pairs
            ]),
        ])
        query_fields += [lit_val for __, lit_val in filter_pairs]

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, query_fields)
        connection.commit()


def increase_row_integer(
    table_name: str,
    set_field: str,
    where_field: str,
    where_value,
):
    """Increase the integer in the row specified by the where fields.

    Given a primary key, a field set_field, and a pair (where_field,
    where_value), it increases the field in the appropriate row

    :param table_name: Primary key to detect workflow

    :param set_field: name of the field to be increased

    :param where_field: Field used to filter the row in the table

    :param where_value: Value of the previous field to filter the row

    :return: The table in the workflow pointed by PK is modified.
    """
    query = sql.SQL('UPDATE {0} SET {1} = {1} + 1 WHERE {2} = %s').format(
        sql.Identifier(table_name),
        sql.Identifier(set_field),
        sql.Identifier(where_field),
        sql.Literal(where_value))

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, [where_value])
        connection.commit()


def select_ids_all_false(
    table_name: str,
    filter_formula: Optional[Dict],
    cond_formula_list: List[Dict],
) -> List[int]:
    """Create query to select rows with all conditions equal to false.

    :param table_name: Table in the DB

    :param filter_formula: Filter formula for the WHERE clause (if any)

    :param cond_formula_list: Non-empty list of condition formulas

    :return: List of indeces for which all conditions (and filter) are false
    """
    # Prelude for the query
    query = sql.SQL(
        'SELECT t.position from ('
        + 'SELECT *, ROW_NUMBER() OVER () '
        + 'AS position FROM {0}) AS t',
    ).format(sql.Identifier(table_name))

    cond_sql, cond_fields = zip(*[
        evaluate_formula(c_formula, NodeEvaluation.EVAL_SQL)
        for c_formula in cond_formula_list
    ])

    # WHERE clause for the conditions
    query = sql.SQL('{0} WHERE {1]').format(
        query,
        sql.SQL('(NOT {0})').format(sql.SQL(') AND (NOT ').join(cond_sql)),
    )
    query_fields = sum(cond_fields, [])

    # Query clause for the filter
    if filter_formula:
        filter_query, filter_fields = evaluate_formula(
            filter_formula,
            NodeEvaluation.EVAL_SQL,
        )
        query = sql.SQL(' AND ').join([query, filter_query])
        query_fields += filter_fields

    # Run the query and return the list
    cursor = connection.cursor()
    cursor.execute(query, query_fields)

    return [id_tuple[0] for id_tuple in cursor.fetchall()]


def get_num_rows(table_name, cond_filter=None):
    """Get the number of rows in the table that satisfy the condition.

    :param table_name: Table name

    :param cond_filter: Formula

    :return: integer
    """
    query = sql.SQL('SELECT count (*) FROM {0}').format(
        sql.Identifier(table_name))

    cond_fields = []
    if cond_filter is not None:
        cond_filter, cond_fields = evaluate_formula(
            cond_filter,
            NodeEvaluation.EVAL_SQL,
        )
        query = sql.SQL('{0} WHERE {1}').format(query, cond_filter)

    with connection.cursor() as cursor:
        cursor.execute(query, cond_fields)
        num_rows = cursor.fetchone()[0]

    return num_rows


def search_table(
    table_name: str,
    search_value: str,
    columns_to_search: Optional[List] = None,
    filter_formula: Optional[Dict] = None,
    any_join: bool = True,
    order_col_name: str = None,
    order_asc: bool = True,
):
    """Search the content of all cells in the table.

    Select rows where for every (column, value) pair, column contains value (
    as in LIKE %value%, these are combined with OR if any is TRUE, or AND if
    any is false, and the result is ordered by the given column and type (if
    given)

    :param table_name: table name

    :param filter_formula: Optional filter condition to pre filter the query

    :param columns_to_search: A column, value, type tuple to search the value
    in the column set. the query is built with these terms as requirement AND
    the cv_tuples.

    :param any_join: Boolean encoding if values should be combined with OR (or
    AND)

    :param order_col_name: Order results by this column

    :param order_asc: Order results in ascending values (or descending)

    :param search_value: String to search

    :return: The resulting query set
    """
    # Create the query
    query = sql.SQL('SELECT {0} FROM {1} WHERE ').format(
        sql.SQL(', ').join([
            sql.Identifier(colname) for colname in columns_to_search
        ]),
        sql.Identifier(table_name),
    )
    query_fields = []

    # Add filter part if present
    if filter_formula:
        filter_query, filter_fields = evaluate_formula(
            filter_formula,
            NodeEvaluation.EVAL_SQL)
        query = sql.SQL('{0} AND ').format(
            sql.SQL('').join([query, filter_query]),
        )
        query_fields += filter_fields

    # Combine the search subqueries
    if any_join:
        conn_txt = ' OR '
    else:
        conn_txt = ' AND '

    # Add the CAST {0} AS TEXT LIKE ...
    query = sql.SQL('').join([
        query,
        sql.SQL('({0})').format(
            sql.SQL(conn_txt).join([
                sql.SQL('(CAST ({0} AS TEXT) LIKE %s)').format(
                    sql.Identifier(cname),
                ) for cname in columns_to_search
            ]),
        ),
    ])
    query_fields += ['%' + search_value + '%'] * len(columns_to_search)

    # Add the order if needed
    if order_col_name:
        query = sql.SQL(' ').join(
            [
                query,
                sql.SQL('ORDER BY {0}').format(sql.Identifier(order_col_name)),
            ],
        )

    if not order_asc:
        query = sql.SQL(' ').join([query, sql.SQL('DESC')])

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, query_fields)
        search_result = cursor.fetchall()

    return search_result


def is_column_in_table(table_name: str, column_name: str) -> bool:
    """Check if a column is in the table.

    :param table_name: Table used for the check

    :param column_name: Column used for the check

    :return: Boolean
    """
    query = sql.SQL(
        'SELECT EXISTS (SELECT 1 FROM information_schema.columns '
        + 'WHERE table_name = {0} AND column_name = {1})',
    ).format(sql.Identifier(table_name), sql.Identifier(column_name))

    with connection.cursor() as cursor:
        cursor.execute(query, [table_name, column_name])
        return cursor.fetchone()[0]


def is_column_table_unique(table_name: str, column_name: str) -> bool:
    """Return if a table column has all non-empty unique values.

    :param table_name: table

    :param column_name: column

    :return: Boolean (is unique)
    """
    query = sql.SQL('SELECT COUNT(DISTINCT {0}) = count(*) from {1}').format(
        sql.Identifier(column_name),
        sql.Identifier(table_name),
    )

    # Get the result
    with connection.cursor() as cursor:
        cursor.execute(query, [])
        return cursor.fetchone()[0]


def delete_table(table_name: str):
    """Delete the given table.

    :param table_name: Table to delete

    :return: Drop the table in the DB
    """
    query = sql.SQL('DROP TABLE {0}').format(sql.Identifier(table_name))

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
    except Exception as exc:
        logger.error(
            'Error when dropping table {tname}: {excmsg}',
            extra={'tname': table_name, 'excmsg': str(exc)},
        )


def get_df_column_types(table_name: str) -> List[str]:
    """Get the list of data types in the given table.

    :param table_name: Table name

    :return: List of SQL types
    """
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL(
            'SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS '
            + 'WHERE TABLE_NAME = {0}').format(sql.Identifier(table_name)))

        type_names = cursor.fetchall()

    return [sql_to_ontask_datatype_names[dtype] for dtype in type_names]


def db_rename_column(table: str, old_name: str, new_name: str):
    """Rename a column in the database.

    :param table: table

    :param old_name: Old name of the column

    :param new_name: New name of the column

    :return: Nothing. Change reflected in the database table
    """
    with connection.cursor() as cursor:
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
    with connection.cursor() as cursor:
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
        sql.Identifier(column_name),
        sql.Literal(''),
        sql.Identifier(table_name),
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]


def delete_row(table_name: str, kv_pair: Tuple[str, Any]):
    """Delete the row with the given key, value pair.

    :param table_name: Table to manipulate

    :param kv_pair: A key=value pair to identify the row. Key is suppose to
    be unique.

    :return: Drops that row from the table in the DB
    """
    # Get the key/value subclause
    bool_clause, query_fields = get_boolean_clause(
        filter_pairs=dict(kv_pair),
    )

    # Create the query
    query = sql.SQL('DELETE FROM {0} WHERE {1}').format(
        sql.Identifier(table_name),
        bool_clause,
    )

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, query_fields)
