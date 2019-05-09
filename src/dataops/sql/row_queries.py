# -*- coding: utf-8 -*-

"""DB queries to manipulate rows."""

from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.db import connection
from psycopg2 import sql
from psycopg2.extras import DictCursor

from dataops.formula import EVAL_SQL, evaluate_formula
from dataops.sql.table_queries import get_boolean_clause, get_select_query


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
        evaluate_formula(c_formula, EVAL_SQL)
        for c_formula in cond_formula_list
    ])

    # WHERE clause for the conditions
    query = sql.SQL('{0} WHERE {1}').format(
        query,
        sql.SQL('(NOT {0})').format(sql.SQL(') AND (NOT ').join(cond_sql)),
    )
    query_fields = sum(cond_fields, [])

    # Query clause for the filter
    if filter_formula:
        filter_query, filter_fields = evaluate_formula(
            filter_formula,
            EVAL_SQL,
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
            EVAL_SQL,
        )
        query = sql.SQL('{0} WHERE {1}').format(query, cond_filter)

    with connection.cursor() as cursor:
        cursor.execute(query, cond_fields)
        num_rows = cursor.fetchone()[0]

    return num_rows


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
