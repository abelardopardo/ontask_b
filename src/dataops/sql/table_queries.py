# -*- coding: utf-8 -*-

"""Direct SQL operations in the DB."""

import logging
from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.db import connection
from psycopg2 import sql

from dataops.formula import EVAL_SQL, evaluate_formula
from ontask import OnTaskDBIdentifier

logger = logging.getLogger('ontask')


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
        clause, clause_fields = evaluate_formula(filter_formula, EVAL_SQL)

    if filter_pairs:
        c_txt = ' AND ' if conjunction else ' OR '
        pairs_clause = sql.SQL(c_txt).join([
            sql.SQL('{0} = {1}').format(
                OnTaskDBIdentifier(key), sql.Placeholder())
            for key, __ in filter_pairs.items()
        ])
        pairs_fields = [lit_val for __, lit_val in filter_pairs.items()]
        if clause:
            clause = clause + sql.SQL(' AND ') + pairs_clause
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
    if column_names:
        query = sql.SQL('SELECT {0} FROM {1}').format(
            sql.SQL(', ').join([
                OnTaskDBIdentifier(cname) for cname in column_names
            ]),
            sql.Identifier(table_name),
        )
    else:
        query = sql.SQL('SELECT * FROM {0}').format(sql.Identifier(table_name))

    query_fields = []

    if filter_formula or filter_pairs:
        bool_clause, query_fields = get_boolean_clause(
            filter_formula=filter_formula,
            filter_pairs=filter_pairs,
        )

        if bool_clause:
            query = query + sql.SQL(' WHERE ') + bool_clause

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
    query = sql.SQL('SELECT {0} FROM {1}').format(
        sql.SQL(', ').join([
            OnTaskDBIdentifier(colname) for colname in columns_to_search
        ]),
        sql.Identifier(table_name),
    )
    query_fields = []

    where_clause = sql.SQL('')
    # Add filter part if present
    if filter_formula:
        filter_query, filter_fields = evaluate_formula(
            filter_formula,
            EVAL_SQL)
        if filter_query:
            where_clause = filter_query
            query_fields += filter_fields

    # Add the CAST {0} AS TEXT LIKE ...
    if search_value:
        if where_clause != sql.SQL(''):
            where_clause = where_clause + sql.SQL(' AND ')

        # Combine the search subqueries
        if any_join:
            conn_txt = ' OR '
        else:
            conn_txt = ' AND '

        where_clause = where_clause + sql.SQL(conn_txt).join([
            sql.SQL('(CAST ({0} AS TEXT) LIKE %s)').format(
                OnTaskDBIdentifier(cname),
            ) for cname in columns_to_search
        ])

        query_fields += ['%' + search_value + '%'] * len(columns_to_search)

    if where_clause != sql.SQL(''):
        query = query + sql.SQL(' WHERE') + where_clause

    # Add the order if needed
    if order_col_name:
        query = query + sql.SQL(' ') + sql.SQL('ORDER BY {0}').format(
            OnTaskDBIdentifier(order_col_name))

    if not order_asc:
        query = query + sql.SQL(' DESC')

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, query_fields)
        search_result = cursor.fetchall()

    return search_result


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
