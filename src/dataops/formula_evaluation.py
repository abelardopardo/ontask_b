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
from builtins import str

import pandas as pd
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext
from psycopg2 import sql

from ontask import OnTaskException


class NodeEvaluation:
    """Class to evaluate the nodes ina formula.

    The methods provide three types of evaluation: python expression,
    SQL query, and text rendering.
    """

    # Type of evaluations for this node
    EVAL_EXP = 0
    EVAL_SQL = 1
    EVAL_TXT = 2

    GET_CONSTANT_FN = {
        'integer': lambda x: int(x),
        'double': lambda x: float(x),
        'boolean': lambda x: True if x else False,
        'string': lambda x: str(x),
        'datetime': lambda x: parse_datetime(x)
    }

    def __init__(self, node, given_variables=None):
        """Create object with expression node and the variable value.

        :param node: Formula leaf node

        :param given_variables: Dictionary with the pairs (varname, varvalue)
        to use to evaluate the expression
        """
        self.node = node
        self.given_variables = given_variables

    @staticmethod
    def is_null(value):
        """Check for null or nan or.

        :param value: Value to check if it is null

        :return: Boolean
        """

        return value is None or pd.isna(value)

    def get_constant(self):
        """Turn node['value']) into right constant (type in node['type']).

        :return: The right Python value
        """
        return self.GET_CONSTANT_FN.get(self.node['type'])(self.node['value'])

    def get_value(self):
        """Return the value to consider for the variable in node['field'].

        :return: The value
        """
        # Get the variable name
        varname = self.node['field']

        varvalue = None
        if self.given_variables is not None:
            # If no value in dictionary, finish
            if varname not in self.given_variables:
                raise OnTaskException(
                    'No value found for variable {0}'.format(varname),
                    0,
                )

            varvalue = self.given_variables.get(varname, None)

        return varvalue

    def get_evaluation(self, eval_type):
        """Evaluate the current node with the type of evaluation given.

        :param eval_type: One of three: EVAL_EXP, EVAL_SQL or EVAL_TXT

        :return: The resulting expression, SQL query or text respectively
        """

        return getattr(self, '_op_' + self.node['operator'])(eval_type)

    def _op_equal(self, eval_type):
        """Process the equal operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue == constant

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} = {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &equals; {1} and not empty'.format(
            self.node['field'], constant,
        )

    def _op_not_equal(self, eval_type):
        """Process the not equal operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue != constant

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} != {1}) OR ({0} is null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder()
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &ne; {1} and not empty'.format(
            self.node['field'], constant,
        )

    def _op_begins_with(self, eval_type):
        """Process the begins_with operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue.startswith(
                constant,
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [self.node['value'] + '%']

            return query, fields

        # Text evaluation
        return '{0} starts with {1}'.format(self.node['field'], constant)

    def _op_not_begins_with(self, eval_type):
        """Process the not_begins_with operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and not varvalue.startswith(
                constant)

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [self.node['value'] + '%']

            return query, fields

        # Text evaluation
        return '{0} does not start with {1}'.format(
            self.node['field'], constant)

    def _op_contains(self, eval_type):
        """Process the contains operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (
                (not self.is_null(varvalue)) and varvalue.find(constant) != -1
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = ['%' + self.node['value'] + '%']

            return query, fields

        # Text evaluation
        return '{0} contains {1}'.format(self.node['field'], constant)

    def _op_not_contains(self, eval_type):
        """Process the not_contains operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (
                (not self.is_null(varvalue)) and varvalue.find(constant) == -1
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = ['%' + self.node['value'] + '%']

            return query, fields

        # Text evaluation
        return '{0} does not contain {1}'.format(self.node['field'], constant)

    def _op_ends_with(self, eval_type):
        """Process the ends_with operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue.endswith(constant)

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = ['%' + self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} ends with {1}'.format(self.node['field'], constant)

    def _op_not_ends_with(self, eval_type):
        """Process the not_ends_width operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (
                (not self.is_null(varvalue))
                and (not varvalue.endswith(constant))
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = ['%' + self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} does not end with {1}'.format(self.node['field'], constant)

    def _op_is_empty(self, eval_type):
        """Process the is_empty operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue == ''

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} = \'\') OR ({0} is null)').format(
                sql.Identifier(self.node['field']),
            )
            fields = [self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} is empty'.format(self.node['field'])

    def _op_is_not_empty(self, eval_type):
        """Process the is_empty operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            return (not self.is_null(varvalue)) and varvalue != ''

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} != \'\') AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
            )
            fields = [self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} is not empty'.format(self.node['field'])

    def _op_is_null(self, eval_type):
        """Process the is_null operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            return self.is_null(self.get_value())

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} is null)').format(
                sql.Identifier(self.node['field']),
            )

            return query, []

        # Text evaluation
        return '{0} is null'.format(self.node['field'])

    def _op_is_not_null(self, eval_type):
        """Process the is_not_null operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            return not self.is_null(self.get_value())

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} is not null)').format(
                sql.Identifier(self.node['field']),
            )

            return query, []

        # Text evaluation
        return '{0} is not null'.format(self.node['field'])

    def _op_less(self, eval_type):
        """Process the less operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.node['type'] in ('integer', 'double', 'datetime'):
                return (not self.is_null(varvalue)) and varvalue < constant
            raise Exception(
                ugettext(
                    'Evaluation error: '
                    + 'Type {0} not allowed with operator LESS',
                ).format(self.node['type']),
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} < {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &lt; {1} and not empty'.format(
            self.node['field'], constant,
        )

    def _op_less_or_equal(self, eval_type):
        """Process the less_or_equal operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.node['type'] in ('integer', 'double', 'datetime'):
                return (not self.is_null(varvalue)) and varvalue <= constant
            raise Exception(
                ugettext(
                    'Evaluation error: Type {0} not allowed '
                    + 'with operator LESS OR EQUAL',
                ).format(self.node['type']),
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} <= {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &#8924; {1} and not empty'.format(
            self.node['field'],
            constant,
        )

    def _op_greater(self, eval_type):
        """Process the greater operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.node['type'] in ('integer', 'double', 'datetime'):
                return (not self.is_null(varvalue)) and varvalue > constant
            raise Exception(
                ugettext(
                    'Evaluation error: Type {0} not allowed '
                    + 'with operator GREATER',
                ).format(self.node['type']),
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} > {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &gt; {1} and not empty'.format(
            self.node['field'], constant,
        )

    def _op_greater_or_equal(self, eval_type):
        """Process the greater_or_equal operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        constant = self.GET_CONSTANT_FN.get(
            self.node['type'],
        )(self.node['value'])

        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.node['type'] in ('integer', 'double', 'datetime'):
                return (not self.is_null(varvalue)) and varvalue >= constant
            raise Exception(
                ugettext(
                    'Evaluation error: Type {0} not allowed '
                    + 'with operator GREATER OR EQUAL',
                ).format(self.node['type']),
            )

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL('({0} >= {1}) AND ({0} is not null)').format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
            )
            fields = [str(constant)]

            return query, fields

        # Text evaluation
        return '{0} &#8925; {1} and not empty'.format(
            self.node['field'],
            constant,
        )

    def _op_between(self, eval_type):
        """Process the between operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.is_null(varvalue):
                return False

            if self.node['type'] not in ('integer', 'double', 'datetime'):
                raise Exception(
                    ugettext(
                        'Evaluation error: Type {0} not allowed '
                        + 'with operator BETWEEN',
                    ).format(self.node['type']),
                )
            left = self.GET_CONSTANT_FN[self.node['type']](
                self.node['value'][0],
            )
            right = self.GET_CONSTANT_FN[self.node['type']](
                self.node['value'][1],
            )

            return left <= varvalue <= right

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL(
                '({0} BETWEEN {1} AND {2}) AND ({0} is not null)',
            ).format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
                sql.Placeholder(),
            )

            fields = [str(num) for num in self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} &#8924; {1} &#8924; {2} and not empty'.format(
            str(self.node['value'][0]),
            self.node['field'],
            str(self.node['value'][1]),
        )

    def _op_not_between(self, eval_type):
        """Process the not_between operator.

        :param eval_type: Type of evaluation

        :return: Boolean result, SQL query, or text result
        """
        if eval_type == self.EVAL_EXP:
            # Python evaluation
            varvalue = self.get_value()
            if self.is_null(varvalue):
                return False

            if self.node['type'] not in ('integer', 'double', 'datetime'):
                raise Exception(
                    ugettext(
                        'Evaluation error: Type {0} not allowed '
                        + 'with operator BETWEEN',
                    ).format(self.node['type']),
                )
            left = self.GET_CONSTANT_FN[self.node['type']](
                self.node['value'][0],
            )
            right = self.GET_CONSTANT_FN[self.node['type']](
                self.node['value'][1],
            )

            return not left <= varvalue <= right

        if eval_type == self.EVAL_SQL:
            # SQL evaluation
            query = sql.SQL(
                '({0} NOT BETWEEN {1} AND {2}) AND ({0} is null)',
            ).format(
                sql.Identifier(self.node['field']),
                sql.Placeholder(),
                sql.Placeholder(),
            )

            fields = [str(number) for number in self.node['value']]

            return query, fields

        # Text evaluation
        return '{0} &lt; {1} or {0} &gt; {2} or {0} is empty'.format(
            self.node['field'],
            str(self.node['value'][0]),
            str(self.node['value'][1]),
        )


def has_variable(formula, var_name):
    """Check if a formula contains a variable.

    It traverses the recursive structure checking for the field "id" in the
    dictionaries.

    :param formula: node element at the top of the formula

    :param var_name: ID to search for

    :return: Boolean encoding if formula has id.
    """
    if 'condition' in formula:
        # Node is a condition, get the values of the sub classes and take a
        # disjunction of the results.

        return any(
            has_variable(sub_f, var_name) for sub_f in formula['rules']
        )

    return var_name == formula['id']


def get_variables(formula):
    """Get a list with the variable names in a formula.

    :param formula:

    :return: list of strings (variable names)
    """
    if 'condition' in formula:
        return list(itertools.chain.from_iterable(
            [get_variables(sub_f) for sub_f in formula['rules']]))

    return [formula['id']]


def rename_variable(formula, old_name, new_name):
    """Rename a variable present in the formula.

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
        formula['rules'] = [
            rename_variable(sub_f, old_name, new_name)
            for sub_f in formula['rules']
        ]
        return formula

    # Loop over the changes and apply them to this node
    if old_name != formula['id']:
        # No need to rename this formula
        return formula

    formula['id'] = new_name
    formula['field'] = new_name

    return formula


def evaluate_formula(node, eval_type, given_variables=None):
    """Evaluate a node depending on the type and with the given variables.

    Given a node representing a formula, and a dictionary with (name, values),
    evaluates the expression represented by the node.

    :param node: Node representing the expression

    :param eval_type: Type of evaluation. See NodeEvaluation: EVAL_EXP is for
    a python expression, EVAL_SQL is a query, and EVAL_TXT a text
    representation of the formula

    :param given_variables: Dictionary (name, value) of variables

    :return: True/False, SQL query or text depending on eval_type
    """
    if 'condition' not in node:
        # Terminal case. Evaluate leave node
        return NodeEvaluation(
            node,
            given_variables,
        ).get_evaluation(eval_type)

    # Node is a COMPOSITION, get the values of the sub-clauses recursively
    sub_clauses = [
        evaluate_formula(sub_formula, eval_type, given_variables)
        for sub_formula in node['rules']]

    # Combine subresults depending on the type of evaluation
    if eval_type == NodeEvaluation.EVAL_EXP:
        if node['condition'] == 'AND':
            result_bool = all(sub_clauses)
        else:
            result_bool = any(sub_clauses)
        if node.get('not', False):
            result_bool = not result_bool
        return result_bool

    join_str = ') ' + node['condition'] + ' ('
    if eval_type == NodeEvaluation.EVAL_SQL:
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

        if node.get('not', False):
            result_query = sql.SQL('NOT ({0})').format(result_query)

        return result_query, result_fields

    # Text evaluation
    if len(sub_clauses) > 1:
        result_txt = '(' + join_str.join(
            [sub_c for sub_c in sub_clauses],
        ) + ')'
    else:
        result_txt = sub_clauses[0]

    if node.get('not', False):
        result_txt = 'NOT (' + result_txt + ')'

    return result_txt
