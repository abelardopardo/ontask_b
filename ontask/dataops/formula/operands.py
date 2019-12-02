# -*- coding: utf-8 -*-

"""Functions to evaluate the operands in OnTask conditions and filters."""
from typing import Any, Dict, Tuple, Union

from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext
import pandas as pd
from psycopg2 import sql

from ontask import OnTaskDBIdentifier, OnTaskException

# Type of evaluations for the formulas
EVAL_EXP = 0
EVAL_SQL = 1
EVAL_TXT = 2

GET_CONSTANT = {
    'integer': lambda operand: int(operand),
    'double': lambda operand: float(operand),
    'boolean': lambda operand: operand == 'true',
    'string': lambda operand: str(operand),
    'datetime': lambda operand: parse_datetime(operand)}


def value_is_null(var_value: Any) -> bool:
    """Check if the value is None or NaN."""
    return var_value is None or pd.isna(var_value)


def get_value(node, given_variables: Dict) -> Any:
    """Return the value to consider for the variable in node['field'].

    :param node: Terminal node in the formula
    :param given_variables: Dictionary with the list of variables/values
    :param given_variables: Dictionary of var/values
    :return: The value
    """
    # Get the variable name
    varname = node['field']

    varvalue = None
    if given_variables is not None:
        # If no value in dictionary, finish
        if varname not in given_variables:
            raise OnTaskException(
                'No value found for variable {0}'.format(varname),
                0,
            )

        varvalue = given_variables.get(varname)
        if isinstance(varvalue, bool):
            varvalue = str(varvalue).lower()

    return varvalue


def equal(
    node,
    eval_type: str,
    given_variables: Dict
) -> Union[str, bool, Tuple]:
    """Process the equal operator.

    :param node: Formula node
    :param eval_type: Type of evaluation
    :param given_variables: Dictionary of var/values
    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue == constant

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} = {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &equals; {1} and not empty'.format(
        node['field'], constant,
    )


def not_equal(node, eval_type, given_variables):
    """Process the not equal operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue != constant

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} != {1}) OR ({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &ne; {1} and not empty'.format(
        node['field'], constant,
    )


def begins_with(node, eval_type, given_variables):
    """Process the begins_with operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue.startswith(
            constant,
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [node['value'] + '%']

        return query, fields

    # Text evaluation
    return '{0} starts with {1}'.format(node['field'], constant)


def not_begins_with(node, eval_type, given_variables):
    """Process the not_begins_with operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and not varvalue.startswith(
            constant)

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [node['value'] + '%']

        return query, fields

    # Text evaluation
    return '{0} does not start with {1}'.format(
        node['field'], constant)


def contains(node, eval_type, given_variables):
    """Process the contains operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (
            (not value_is_null(varvalue)) and varvalue.find(constant) != -1
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = ['%' + node['value'] + '%']

        return query, fields

    # Text evaluation
    return '{0} contains {1}'.format(node['field'], constant)


def not_contains(node, eval_type, given_variables):
    """Process the not_contains operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (
            (not value_is_null(varvalue)) and varvalue.find(constant) == -1
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = ['%' + node['value'] + '%']

        return query, fields

    # Text evaluation
    return '{0} does not contain {1}'.format(node['field'], constant)


def ends_with(node, eval_type, given_variables):
    """Process the ends_with operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue.endswith(constant)

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} LIKE {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = ['%' + node['value']]

        return query, fields

    # Text evaluation
    return '{0} ends with {1}'.format(node['field'], constant)


def not_ends_with(node, eval_type, given_variables):
    """Process the not_ends_width operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (
            (not value_is_null(varvalue))
            and (not varvalue.endswith(constant))
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} NOT LIKE {1}) OR ({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = ['%' + node['value']]

        return query, fields

    # Text evaluation
    return '{0} does not end with {1}'.format(node['field'], constant)


def is_empty(node, eval_type, given_variables):
    """Process the is_empty operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue == ''

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} = \'\') OR ({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
        )

        return query, []

    # Text evaluation
    return '{0} is empty'.format(node['field'])


def is_not_empty(node, eval_type, given_variables):
    """Process the is_empty operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        return (not value_is_null(varvalue)) and varvalue != ''

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} != \'\') AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
        )

        return query, []

    # Text evaluation
    return '{0} is not empty'.format(node['field'])


def is_null(node, eval_type, given_variables):
    """Process the is_null operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        node_value = get_value(node, given_variables)
        return value_is_null(node_value)

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} is null)').format(
            OnTaskDBIdentifier(node['field']),
        )

        return query, []

    # Text evaluation
    return '{0} is null'.format(node['field'])


def is_not_null(node, eval_type, given_variables):
    """Process the is_not_null operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        return not value_is_null(get_value(node, given_variables))

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
        )

        return query, []

    # Text evaluation
    return '{0} is not null'.format(node['field'])


def less(node, eval_type, given_variables):
    """Process the less operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if node['type'] in ('integer', 'double', 'datetime'):
            return (not value_is_null(varvalue)) and varvalue < constant
        raise Exception(
            ugettext(
                'Evaluation error: '
                + 'Type {0} not allowed with operator LESS',
            ).format(node['type']),
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} < {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &lt; {1} and not empty'.format(
        node['field'], constant,
    )


def less_or_equal(node, eval_type, given_variables):
    """Process the less_or_equal operator.

    :param node: Formula node

    :param eval_type: Type of evaluation

    :param given_variables: Dictionary of var/values

    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if node['type'] in ('integer', 'double', 'datetime'):
            return (not value_is_null(varvalue)) and varvalue <= constant
        raise Exception(
            ugettext(
                'Evaluation error: Type {0} not allowed '
                + 'with operator LESS OR EQUAL',
            ).format(node['type']),
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} <= {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &#8924; {1} and not empty'.format(
        node['field'],
        constant,
    )


def greater(
    node,
    eval_type: str,
    given_variables: Dict
) -> Union[bool, str, Tuple]:
    """Process the greater operator.

    :param node: Formula node
    :param eval_type: Type of evaluation
    :param given_variables: Dictionary of var/values
    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if node['type'] in ('integer', 'double', 'datetime'):
            return (not value_is_null(varvalue)) and varvalue > constant
        raise Exception(
            ugettext(
                'Evaluation error: Type {0} not allowed '
                + 'with operator GREATER',
            ).format(node['type']),
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} > {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &gt; {1} and not empty'.format(
        node['field'], constant,
    )


def greater_or_equal(
    node,
    eval_type: str,
    given_variables: Dict
) -> Union[bool, str, Tuple]:
    """Process the greater_or_equal operator.

    :param node: Formula node
    :param eval_type: Type of evaluation
    :param given_variables: Dictionary of var/values
    :return: Boolean result, SQL query, or text result
    """
    constant = GET_CONSTANT.get(node['type'])(node['value'])

    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if node['type'] in ('integer', 'double', 'datetime'):
            return (not value_is_null(varvalue)) and varvalue >= constant
        raise Exception(
            ugettext(
                'Evaluation error: Type {0} not allowed '
                + 'with operator GREATER OR EQUAL',
            ).format(node['type']),
        )

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL('({0} >= {1}) AND ({0} is not null)').format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
        )
        fields = [str(constant)]

        return query, fields

    # Text evaluation
    return '{0} &#8925; {1} and not empty'.format(
        node['field'],
        constant,
    )


def between(
    node,
    eval_type: str,
    given_variables: Dict
) -> Union[bool, str, Tuple]:
    """Process the between operator.

    :param node: Formula node
    :param eval_type: Type of evaluation
    :param given_variables: Dictionary of var/values
    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if value_is_null(varvalue):
            return False

        if node['type'] not in ('integer', 'double', 'datetime'):
            raise Exception(
                ugettext(
                    'Evaluation error: Type {0} not allowed '
                    + 'with operator BETWEEN',
                ).format(node['type']),
            )
        left = GET_CONSTANT[node['type']](node['value'][0])
        right = GET_CONSTANT[node['type']](node['value'][1])

        return left <= varvalue <= right

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL(
            '({0} BETWEEN {1} AND {2}) AND ({0} is not null)',
        ).format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
            sql.Placeholder(),
        )

        fields = [str(num) for num in node['value']]

        return query, fields

    # Text evaluation
    return '{0} &#8924; {1} &#8924; {2} and not empty'.format(
        str(node['value'][0]),
        node['field'],
        str(node['value'][1]),
    )


def not_between(
    node,
    eval_type: str,
    given_variables: Dict,
) -> Union[bool, str, Tuple]:
    """Process the not_between operator.

    :param node: Formula node
    :param eval_type: Type of evaluation
    :param given_variables: Dictionary of var/values
    :return: Boolean result, SQL query, or text result
    """
    if eval_type == EVAL_EXP:
        # Python evaluation
        varvalue = get_value(node, given_variables)
        if value_is_null(varvalue):
            return False

        if node['type'] not in ('integer', 'double', 'datetime'):
            raise Exception(
                ugettext(
                    'Evaluation error: Type {0} not allowed '
                    + 'with operator BETWEEN',
                ).format(node['type']),
            )
        left = GET_CONSTANT[node['type']](node['value'][0])
        right = GET_CONSTANT[node['type']](node['value'][1])

        return not left <= varvalue <= right

    if eval_type == EVAL_SQL:
        # SQL evaluation
        query = sql.SQL(
            '({0} NOT BETWEEN {1} AND {2}) AND ({0} is not null)',
        ).format(
            OnTaskDBIdentifier(node['field']),
            sql.Placeholder(),
            sql.Placeholder(),
        )

        fields = [str(number) for number in node['value']]

        return query, fields

    # Text evaluation
    return '{0} &lt; {1} or {0} &gt; {2} or {0} is empty'.format(
        node['field'],
        str(node['value'][0]),
        str(node['value'][1]),
    )
