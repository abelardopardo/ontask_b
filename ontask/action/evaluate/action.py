# -*- coding: utf-8 -*-

"""Functions to evaluate actions based on the values in the table.

- evaluate_action: Evaluates the content of an action

- evaluate_row_action_out: Evaluates an action text for a single row of the
  table

"""

from builtins import str
from datetime import datetime
from typing import Dict, List, Mapping, Optional, Tuple, Union

from django.conf import settings
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import ontask
from ontask import models
from ontask.action.evaluate.template import render_action_template
from ontask.dataops.formula import EVAL_EXP, evaluate_formula
from ontask.dataops.pandas import get_table_row_by_index
from ontask.dataops.sql.row_queries import get_row, get_rows


def _render_tuple_result(
    action: models.Action,
    context: Dict[str, Union[str, float, int, datetime]],
    extra_string: str,
    column_name: str,
) -> List:
    """Render text in action, extra string (optional), and get column_name.

    Render the content in the action, render the extra string if given, and
    add the value of the column_name. All this with the values in the context
    :param action: Action object
    :param context: Dictionary with name: value
    :param extra_string: Optional string to render
    :param column_name: Column name to include its value
    :return: [action content render, extra string rendered (optional),
              column value (optional)]
    """
    # Run the template with the given context
    partial_result = [render_action_template(
        action.text_content,
        context,
        action,
    )]

    # If there is extra message, render with context and append
    if extra_string:
        partial_result.append(render_action_template(extra_string, context))

    # If column_name was given (and it exists), add as third component
    if column_name and column_name in context:
        partial_result.append(context[column_name])

    return partial_result


def action_condition_evaluation(
    action: models.Action,
    row_values: Mapping,
) -> Optional[Dict[str, bool]]:
    """Calculate dictionary with column_name: Boolean evaluations.

    :param action: Action objects to obtain the columns
    :param row_values: dictionary with (name: value) pairs for one row
    :return: Dictionary condition_name: True/False or None if anomaly
    """
    condition_eval = {}
    conditions = action.conditions.filter(is_filter=False).values(
        'name', 'is_filter', 'formula',
    )
    for condition in conditions:
        # Evaluate the condition
        try:
            condition_eval[condition['name']] = evaluate_formula(
                condition['formula'],
                EVAL_EXP,
                row_values,
            )
        except ontask.OnTaskException:
            # Something went wrong evaluating a condition. Stop.
            return None
    return condition_eval


def get_action_evaluation_context(
    action: models.Action,
    row_values: Mapping,
    condition_eval: Mapping = None,
) -> Optional[Dict]:
    """Create a dictionary with name:value to evaluate action content.

    :param action: Action object for which the dictionary is needed
    :param row_values: Dictionary with col_name, col_value
    :param condition_eval: Dictionary with the condition evaluations
    :return: Dictionary with context values or None if there is an anomaly
    """
    # If no row values are given, there is nothing to do here.
    if row_values is None:
        # No rows satisfy the given condition
        return None

    if not condition_eval:
        # Step 1: Evaluate all the conditions
        condition_eval = {}
        conditions = action.conditions.filter(is_filter=False).values(
            'name', 'is_filter', 'formula',
        )
        for condition in conditions:
            # Evaluate the condition
            try:
                condition_eval[condition['name']] = evaluate_formula(
                    condition['formula'],
                    EVAL_EXP,
                    row_values,
                )
            except ontask.OnTaskException:
                # Something went wrong evaluating a condition. Stop.
                return None

    # Create the context with the attributes, the evaluation of the
    # conditions and the values of the columns.
    return dict(
        dict(row_values, **condition_eval),
        **action.workflow.attributes,
    )


def evaluate_action(
    action: models.Action,
    extra_string: str = None,
    column_name: str = None,
    exclude_values: List[str] = None,
) -> List[List]:
    """Evaluate the content in an action based on the values in the columns.

    Given an action object and an optional string:
    1) Access the attached workflow
    2) Obtain the data from the appropriate data frame
    3) Loop over each data row and
      3.1) Evaluate the conditions with respect to the values in the row
      3.2) Create a context with the result of evaluating the conditions,
           attributes and column names to values
      3.3) Run the template with the context
      3.4) Run the optional string argument with the template and the context
      3.5) Select the optional column_name
    4) Return the resulting objects:
       List of (HTMLs body, extra string, column name value)
        or an error message

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :param extra_string: An extra string to process (something like the email
           subject line) with the same dictionary as the text in the action.
    :param column_name: Column from where to extract the special value (
           typically the email address) and include it in the result.
    :param exclude_values: List of values in the column to exclude
    :return: list of lists resulting from the evaluation of the action. Each
             element in the list contains the HTML body, the extra string (if
             provided) and the column value.
    """
    # Get the table data
    rows = get_rows(
        action.workflow.get_data_frame_table_name(),
        filter_formula=action.get_filter_formula())
    list_of_renders = []
    for row in rows:
        if exclude_values and str(row[column_name]) in exclude_values:
            # Skip the row with the col_name in exclude values
            continue

        # Step 4: Create the context with the attributes, the evaluation of the
        # conditions and the values of the columns.
        context = get_action_evaluation_context(action, row)

        # Append result
        list_of_renders.append(
            _render_tuple_result(action, context, extra_string, column_name),
        )

    if settings.DEBUG:
        # Check that n_rows_selected is equal to rows.rowcount
        action_filter = action.get_filter()
        if action_filter and action_filter.n_rows_selected != rows.rowcount:
            raise ontask.OnTaskException('Inconsistent n_rows_selected')

    return list_of_renders


def get_row_values(
    action: models.Action,
    row_idx: Union[int, Tuple[str, str]],
) -> Dict[str, Union[str, int, float, datetime]]:
    """Get the values in a row either by index or by key.

    Given an action and a row index, obtain the appropriate row of values
    from the data frame.

    :param action: Action object
    :param row_idx: Row index to use for evaluation
    :return Dictionary with the data row
    """
    # Step 1: Get the row of data from the DB
    filter_formula = action.get_filter_formula()

    # If row_idx is an integer, get the data by index, otherwise, by key
    if isinstance(row_idx, int):
        row = get_table_row_by_index(
            action.workflow,
            filter_formula,
            row_idx,
        )
    else:

        row = get_row(
            action.workflow.get_data_frame_table_name(),
            row_idx[0],
            row_idx[1],
            column_names=action.workflow.get_column_names(),
            filter_formula=filter_formula,
        )
    return row


def evaluate_row_action_out(
    action: models.Action,
    context: Mapping,
    text: str = None,
) -> Optional[str]:
    """Evaluate the text in an action out based on the values in a context.

    Given an action object and a row index:
    1) Evaluate the conditions with respect to the values in the row
    2) Create a context with the result of evaluating the conditions,
       attributes and column names to values
    3) Run the template with the context
    4) Return the resulting object (HTML?)

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :param context: dictionary with the pairs name, value for the columns,
    attributes and conditions (true/false)
    :param text: If given, the text is processed in the template, if not
    action_content is used
    :return: String with the HTML content resulting from the evaluation
    """
    # If context is None, propagate.
    if context is None:
        return None

    # Invoke the appropriate function depending on the action type
    if action.is_in:
        raise Exception(_('Incorrect type of action'))

    if text is None:
        # If the text is not given, take the one in the action
        text = action.text_content

    # Run the template with the given context
    # First create the template with the string stored in the action
    try:
        action_text = render_action_template(text, context, action)
    except TemplateSyntaxError as exc:
        return render_to_string('action/syntax_error.html', {'msg': str(exc)})

    return action_text
