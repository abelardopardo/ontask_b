# -*- coding: utf-8 -*-

"""Functions to evaluate the formulas in OnTask.

There are three possible evaluation types:

- Conventional Boolean evalaution: Done with a set of values and returns
either true or false.

- SQL Evaluation: Returns a SQL query object suitable to be sent to the DB
for execution.

- Text rendering: Render a formula to a readable format.
"""
import itertools
from typing import Dict, List, Optional, Tuple, Union

from psycopg2 import sql

from ontask.dataops.formula import operands


def evaluate_formula(
    node,
    eval_type: str,
    given_variables: Optional[Dict] = None,
) -> Union[bool, Tuple[str, List]]:
    """Evaluate a node depending on the type and with the given variables.

    Given a node representing a formula, and a dictionary with (name, values),
    evaluates the expression represented by the node.

    :param node: JSON node representing the expression
    :param eval_type: Type of evaluation. See NodeEvaluation: EVAL_EXP is for
    a python expression, EVAL_SQL is a query, and EVAL_TXT a text
    representation of the formula
    :param given_variables: Dictionary (name, value) of variables
    :return: True/False, (SQL query, fields) or string depending on eval_type
    """
    if 'condition' not in node:
        # Terminal case. Evaluate leave node
        return getattr(
            operands,
            node['operator'])(node, eval_type, given_variables)

    # Node is a COMPOSITION, get the values of the sub-clauses recursively
    sub_clauses = [
        evaluate_formula(sub_formula, eval_type, given_variables)
        for sub_formula in node['rules']]

    # Combine subresults depending on the type of evaluation
    if eval_type == operands.EVAL_EXP:
        if node['condition'] == 'AND':
            result_bool = all(sub_clauses)
        else:
            result_bool = any(sub_clauses)
        if node.get('not') is True:
            result_bool = not result_bool
        return result_bool

    join_str = ') ' + node['condition'] + ' ('
    if eval_type == operands.EVAL_SQL:
        if not sub_clauses:
            # Nothing has been returned, so it is an empty query
            return '', []

        result_query = sql.SQL('({0})').format(
            sql.SQL(join_str).join(
                [sub_c for sub_c, __ in sub_clauses],
            ),
        )
        result_fields = list(itertools.chain.from_iterable(
            [sub_field for __, sub_field in sub_clauses]))

        if node.get('not') is True:
            result_query = sql.SQL('NOT ({0})').format(result_query)

        return result_query, result_fields

    # Text evaluation
    if not sub_clauses:
        return ''

    if len(sub_clauses) > 1:
        result_txt = '(' + join_str.join(
            [sub_c for sub_c in sub_clauses],
        ) + ')'
    else:
        result_txt = sub_clauses[0]

    if node.get('not') is True:
        result_txt = 'NOT (' + result_txt + ')'

    return result_txt


def has_variable(node, var_name):
    """Check if a formula contains a variable.

    It traverses the recursive structure checking for the field "id" in the
    dictionaries.

    :param node: node element at the top of the formula
    :param var_name: ID to search for
    :return: Boolean encoding if formula has id.
    """
    if 'condition' in node:
        # Node is a condition, get the values of the sub classes and take a
        # disjunction of the results.

        return any(
            has_variable(sub_f, var_name) for sub_f in node['rules']
        )

    return var_name == node['id']


def get_variables(node):
    """Get a list with the variable names in a formula.

    :param node:
    :return: list of strings (variable names)
    """
    if 'condition' in node:
        return list(itertools.chain.from_iterable(
            [get_variables(sub_f) for sub_f in node['rules']]))

    return [node['id']]


def rename_variable(node, old_name, new_name):
    """Rename a variable present in the formula.

    Function that traverses the formula and changes the appearance of one
    variable. The renaming is done to the values of the id and field
     attributes.

    :param node: Root node of the formula object
    :param old_name: Old variable name
    :param new_name: New variable name
    :return: The new modified formula.
    """
    # Trivial case of an empty formula
    if not node:
        return node

    if 'condition' in node:
        # Recursive call
        node['rules'] = [
            rename_variable(sub_f, old_name, new_name)
            for sub_f in node['rules']
        ]
        return node

    # Loop over the changes and apply them to this node
    if old_name != node['id']:
        # No need to rename this formula
        return node

    node['id'] = new_name
    node['field'] = new_name

    return node
