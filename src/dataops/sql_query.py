# -*- coding: utf-8 -*-

"""Direct SQL operations in the DB."""

from typing import Dict, List, Tuple, Union, Optional

import psycopg2.extras
from django.db import connection
from psycopg2 import sql
from psycopg2.sql import Composed

from dataops.formula_evaluation import NodeEvaluation, evaluate_formula


sql_to_ontask_datatype_names = {
    'text': 'string',
    'bigint': 'integer',
    'double precision': 'double',
    'boolean': 'boolean',
    'timestamp with time zone': 'datetime'
}

ontask_to_sql_datatype_names = {
    val: key for key, val in sql_to_ontask_datatype_names.items()
}


def add_column(
    table_name: str,
    col_name: str,
    col_type: str,
    initial=None
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


def add_column_integer(table_name: str, col_name: str, initial: int = 0):
    """Add an extra column of type integer with initial value.

    :param table_name: Table to consider
    :param col_name: Column name
    :param initial: initial value
    :return:
    """
    query = sql.SQL(
        'ALTER TABLE {0} ADD COLUMN {1} INTEGER DEFAULT {2}'
    ).format(
        sql.Identifier(table_name),
        sql.Identifier(col_name),
        sql.Literal(initial),
    )
    connection.cursor().execute(query)


def select_id_all_false(
    table_name: str,
    filter_formula: Dict,
    cond_formula_list: List[Dict],
) -> Tuple[Composed, List[str]]:
    """Select rows in table with all conditions equal to false."""
    cond_sql = ''
    cond_fields = []
    if filter_formula:
        cond_sql, cond_fields = evaluate_formula(
            filter_formula,
            NodeEvaluation.EVAL_SQL,
        )
        cond_sql += ' AND '

    # Calculate the evaluation of each of the conditions
    cond_list_sql = [
        evaluate_formula(c_formula, NodeEvaluation.EVAL_SQL)
        for c_formula in cond_formula_list
    ]

    cond_sql += '(NOT ' + ') AND (NOT '.join(
        [cond for cond, __ in cond_list_sql],
    ) + ')'
    cond_fields += sum(
        [sql_field for __, sql_field in cond_list_sql],
        [],
    )

    query = sql.SQL(
        'SELECT t.position from ('
        + 'SELECT *, ROW_NUMBER() OVER () '
        + 'as position FROM {0}) as t WHERE {1}').format(
        sql.Identifier(table_name),
        sql.SQL(cond_sql),
    )

    return query, cond_fields


def get_table_select_cursor(
    table_name: str,
    filter_formula,
    column_names: Optional[List[str]] = None,
):
    """Get a DB cursor with the result of a SELECT query for a single row.

    Execute a select query in the database with an optional filter obtained
    from the jquery QueryBuilder.

    :param table_name: Primary key of the workflow storing the data
    :param filter_formula: JSON formula or None
    :param column_names: optional list of columns to select
    :return: cursor resulting from the query
    """
    if not column_names:
        column_names = ['*']

    # Create the query
    query = sql.SQL('SELECT {0} from {1}').format(
        sql.SQL(', ').join(
            [sql.Identifier(cname) for cname in column_names]
        ),
        sql.Identifier(table_name),
    )

    # See if the action has a filter or not
    fields = []
    if filter_formula:
        filter_formula, fields = evaluate_formula(
            filter_formula.formula,
            NodeEvaluation.EVAL_SQL,
        )
        if filter_formula:
            query = sql.SQL(' WHERE ').join([query, filter_formula])

    # Execute the query
    return connection.connection.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    ).execute(query, fields)


