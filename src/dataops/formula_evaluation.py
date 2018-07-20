# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import itertools

from django.utils.dateparse import parse_datetime

from ontask import OntaskException, fix_pctg_in_name


def has_variable(formula, variable):
    """
    Function that detects if a formula contains an ID. It traverses the
    recursive structure checking for the field "id" in the dictionaries.

    :param formula: node element at the top of the formula
    :param variable: ID to search for
    :return: Boolean encoding if formula has id.
    """

    if 'condition' in formula:
        # Node is a condition, get the values of the sub clases and take a
        # disjunction of the results.

        return any([has_variable(x, variable) for x in formula['rules']])

    return formula['id'] == variable


def get_variables(formula):
    """
    Return a list with the variable names in a formula
    :param formula:
    :return: list of strings (variable names)
    """

    if 'condition' in formula:
        return list(itertools.chain.from_iterable(
            [get_variables(x) for x in formula['rules']]
        ))

    return [formula['id']]


def rename_variable(formula, old_name, new_name):
    """
    Function that traverses the formula and changes the appearance of one
    variable. The renaming is done to the values of the id and field
     attributes.
    :param formula: Root node of the formula object
    :param old_name: Old variable name
    :param new_name: New variable name
    :return: The new modified formula.
    """

    # Trivial case of an empty formula
    if not formula:
        return formula

    if 'condition' in formula:
        # Recursive call
        formula['rules'] = [rename_variable(x, old_name, new_name)
                            for x in formula['rules']]
        return formula

    # Loop over the changes and apply them to this node
    if formula['id'] != old_name:
        # No need to rename this formula
        return formula

    formula['id'] = new_name
    formula['field'] = new_name

    return formula


def evaluate_top_node(query_obj, given_vars):
    """
    Given a json_string and a dictionary with (varname, varvalue),
    it parses the string and returns the True/False result.
    :param query_obj: Object produced by jQuery QueryBuilder
    :param given_vars: Dictionary of (varname, varvalue) for the evaluation
    :return: True/False
    """
    # Pop the "valid" field. It should always be true anyway
    # query_obj.pop('valid')

    return evaluate_node(query_obj, given_vars)


def evaluate_node(node, given_variables):
    """
    Given a node representing a query, and a dictionary with (name, values),
    evaluates the expression represented by the node.
    :param node: Node representing the expression
    :param given_variables: Dictionary (name, value) of variables
    :return: True/False depending on the evaluation
    """
    if 'condition' in node:
        # Node is a condition, get the values of the sub-clauses
        sub_clauses = [evaluate_node(x, given_variables)
                       for x in node['rules']]

        # Now combine
        if node['condition'] == 'AND':
            result = all(sub_clauses)
        else:
            result = any(sub_clauses)

        if node.get('not', False):
            result = not result

        return result

    # Get the variable name
    varname = node['field']
    # Get the variable value if running in boolean mode
    varvalue = None
    if given_variables is not None:
        # If calculating a boolean result and no value in the dictionary, finish
        if varname not in given_variables:
            raise OntaskException(
                'No value found for variable {0}'.format(varname),
                varname
            )

        varvalue = given_variables.get(varname, None)

    # Get the operator
    operator = node['operator']

    # If the operator is between or not_between, there is a special case,
    # the constant cannot be computed because the node['value'] is a pair
    constant = None
    if 'between' not in operator:
        # Calculate the constant value depending on the type
        if node['type'] == 'integer':
            constant = int(node['value'])
        elif node['type'] == 'double':
            constant = float(node['value'])
        elif node['type'] == 'boolean':
            constant = node['value'] == '1'
        elif node['type'] == 'string':
            constant = str(node['value'])
        elif node['type'] == 'datetime':
            constant = parse_datetime(node['value'])
        else:
            raise Exception('No function to translate type', node['type'])

    # Terminal Node
    if operator == 'equal':
        result = varvalue == constant

    elif operator == 'not_equal':
        result = varvalue != constant

    elif operator == 'begins_with' and node['type'] == 'string':
        result = (varvalue is not None) and varvalue.startswith(constant)

    elif operator == 'not_begin_with' and node['type'] == 'string':
        result = not ((varvalue is not None) and varvalue.startswith(constant))

    elif operator == 'contains' and node['type'] == 'string':
        result = (varvalue is not None) and varvalue.find(constant) != -1

    elif operator == 'not_contains' and node['type'] == 'string':
        result = (varvalue is None) or varvalue.find(constant) == -1

    elif operator == 'ends_with' and node['type'] == 'string':
        result = (varvalue is not None) and varvalue.endswith(constant)

    elif operator == 'not_ends_width' and node['type'] == 'string':
        result = (varvalue is None) or (not varvalue.endswith(constant))

    elif operator == 'is_empty' and node['type'] == 'string':
        result = varvalue == '' or varvalue == None

    elif operator == 'is_not_empty' and node['type'] == 'string':
        result = (varvalue is not None) and varvalue != ''

    elif operator == 'less' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = varvalue < constant

    elif operator == 'less_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = varvalue <= constant

    elif operator == 'greater' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = varvalue > constant

    elif operator == 'greater_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = varvalue >= constant

    elif operator == 'between' or operator == 'not_between':
        if node['type'] == 'integer':
            left = int(node['value'][0])
            right = int(node['value'][1])
        elif node['type'] == 'double':
            left = float(node['value'][0])
            right = float(node['value'][1])
        elif node['type'] == 'datetime':
            left = parse_datetime(node['value'][0])
            right = parse_datetime(node['value'][1])
        else:
            raise Exception('Incorrect data type')

        result = left <= varvalue <= right
        if operator == 'not_between':
            result = not result

    else:
        raise Exception('Type, operator, field',
                        node['type'], operator, varname,
                        'not supported yet.')

    if node.get('not', False):
        raise Exception('Negation found in unexpected location')

    return result


def evaluate_node_sql(node):
    """
    Given a node representing a query filter
    translates the expression into a SQL filter expression.
    :param node: Node representing the expression
    :return: String with the filter and list of fields to replace

    WARNING:
    select * from table where variable <> 'value'
    does not return records where variable is different from value. It ignores
    those that are NULL

    Instead the query should be:

    select * from table where (variable <> 'value') or (variable is null)

    """
    if 'condition' in node:
        # Node is a condition, get the values of the sub-clauses
        sub_pairs = \
            [evaluate_node_sql(x) for x in node['rules']]

        if not sub_pairs:
            # Nothing has been returned, so it is an empty query
            return '', []

        # Now combine
        if node['condition'] == 'AND':
            result = '((' + \
                     ') AND ('.join([x for x, __ in sub_pairs]) + '))'
        else:
            result = '((' + \
                     ') OR ('.join([x for x, __ in sub_pairs]) + '))'
        result_fields = \
            list(itertools.chain.from_iterable([x for __, x in sub_pairs]))

        if node.get('not', False):
            result = '(NOT (' + result + '))'

        return result, result_fields

    # Get the variable name and duplicate the symbol % in case it is part of
    # the variable name (escape needed for SQL processing)
    varname = fix_pctg_in_name(node['field'])

    # Get the operator
    operator = node['operator']

    # If the operator is between or not_between, there is a special case,
    # the constant cannot be computed because the node['value'] is a pair
    constant = None
    if 'between' not in operator:
        # Calculate the constant value depending on the type
        if node['type'] == 'integer':
            constant = int(node['value'])
        elif node['type'] == 'double':
            constant = float(node['value'])
        elif node['type'] == 'boolean':
            constant = int(node['value'] == '1')
        elif node['type'] == 'string':
            constant = node['value']
        elif node['type'] == 'datetime':
            constant = node['value']
        else:
            raise Exception('No function to translate type', node['type'])

    # Terminal Node
    result_fields = []
    if operator == 'equal':
        result = '("{0}"'.format(varname) + \
                 ' = %s) AND ("{0}" is not null)'.format(varname)
        result_fields = [str(constant)]

    elif operator == 'not_equal':
        result = '("{0}"'.format(varname) + \
                 '!= %s) OR ("{0}" is null)'.format(varname)
        result_fields = [str(constant)]

    elif operator == 'begins_with' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' LIKE %s) AND ("{0}" is not null)'.format(varname)
        result_fields = [node['value'] + "%"]

    elif operator == 'not_begins_with' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' NOT LIKE %s) OR ("{0}" is null)'.format(varname)
        result_fields = [node['value'] + "%"]

    elif operator == 'contains' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' LIKE %s) AND ("{0}" is not null)'.format(varname)
        result_fields = ["%" + node['value'] + "%"]

    elif operator == 'not_contains' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' NOT LIKE %s) OR ("{0}" is null)'.format(varname)
        result_fields = ["%" + node['value'] + "%"]

    elif operator == 'ends_with' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' LIKE %s) AND ("{0}" is not null)'.format(varname)
        result_fields = ["%" + node['value']]

    elif operator == 'not_ends_width' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 ' NOT LIKE %s) OR ("{0}" is null)'.format(varname)
        result_fields = ["%" + node['value']]

    elif operator == 'is_empty' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 " = '') OR (\"{0}\" is null)".format(varname)

    elif operator == 'is_not_empty' and node['type'] == 'string':
        result = '("{0}"'.format(varname) + \
                 " != '') AND (\"{0}\" is not null)".format(varname)

    elif operator == 'less' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' < %s'
        result_fields = [str(constant)]

    elif operator == 'less_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' <= %s'
        result_fields = [str(constant)]

    elif operator == 'greater' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' > %s'
        result_fields = [str(constant)]

    elif operator == 'greater_or_equal' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' >= %s'
        result_fields = [str(constant)]

    elif operator == 'between' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' BETWEEN %s AND %s'
        result_fields = [str(node['value'][0]), str(node['value'][1])]

    elif operator == 'not_between' and \
            (node['type'] == 'integer' or node['type'] == 'double'
             or node['type'] == 'datetime'):
        result = '"{0}"'.format(varname) + ' NOT BETWEEN %s AND %s'
        result_fields = [str(node['value'][0]), str(node['value'][1])]

    else:
        raise Exception('Type, operator, field',
                        node['type'], operator, varname,
                        'not supported yet.')

    if node.get('not', False):
        raise Exception('Negation found in unexpected location')

    return result, result_fields
