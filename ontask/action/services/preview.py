# -*- coding: utf-8 -*-

"""Process requests to preview how an action is rendered."""
import json
from json.decoder import JSONDecodeError
from typing import Dict, Mapping, Optional, Tuple

from django.template.base import Template
from django.template.context import Context
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.action import forms
from ontask.action.evaluate import (
    action_condition_evaluation, evaluate_row_action_out,
    get_action_evaluation_context, get_row_values,
)


def _check_json_is_correct(text_content: str) -> bool:
    """Check the given string is a correct JSON object.

    :param text_content: String to consider
    :return: Boolean stating correctness
    """
    try:
        json.loads(text_content)
    except JSONDecodeError:
        return False
    return True


def _get_navigation_index(idx: int, n_items: int) -> Tuple[int, int, int]:
    """Given the index and number of items calculate idx, prev and nex.

    Function that given an index and the number of items, adjusts the index to
    the correct value and computers previous and next values.

    :param n_items: Integer with the number of items being considered
    """
    # Set the idx to a legal value just in case
    if not 1 <= idx <= n_items:
        idx = 1

    prv = idx - 1
    if prv <= 0:
        prv = n_items

    nxt = idx + 1
    if nxt > n_items:
        nxt = 1

    return prv, idx, nxt


def _evaluate_row_action_in(action: models.Action, context: Mapping):
    """Evaluate an action_in in the given context.

    Given an action IN object and a row index:
    1) Create the form and the context
    2) Run the template with the context
    3) Return the resulting object (HTML?)

    :param action: Action object.
    :param context: Dictionary with pairs name/value
    :return: String with the HTML content resulting from the evaluation
    """
    # Get the active columns attached to the action
    tuples = [
        column_condition_pair
        for column_condition_pair in action.column_condition_pair.all()
        if column_condition_pair.column.is_active
    ]

    col_values = [context[colcon_pair.column.name] for colcon_pair in tuples]

    form = forms.EnterActionIn(
        None,
        tuples=tuples,
        context=context,
        values=col_values)

    # Render the form
    return Template(
        """<div align="center">
             <p class="lead">{{ description_text }}</p>
             {% load crispy_forms_tags %}{{ form|crispy }}
           </div>""",
    ).render(Context(
        {
            'form': form,
            'description_text': action.description_text,
        },
    ))


def create_row_preview_context(
    action: models.Action,
    idx: int,
    context: Dict,
    prelude: Optional[str] = None,
):
    """Create the elements to render a single row preview.

    :param action: Action being previewed.
    :param idx:
    :param context:
    :param prelude: Optional additional text to include in the preview.
    :return: context is modified to include the appropriate items
    """
    # Get the total number of items
    filter_obj = action.get_filter()
    if filter_obj:
        n_items = filter_obj.n_rows_selected
    else:
        n_items = action.workflow.nrows

    # Set the correct values to the indeces
    prv, idx, nxt = _get_navigation_index(idx, n_items)

    row_values = get_row_values(action, idx)

    # Obtain the dictionary with the condition evaluation
    condition_evaluation = action_condition_evaluation(action, row_values)
    # Get the dictionary containing column names, attributes and condition
    # valuations:
    eval_context = get_action_evaluation_context(
        action,
        row_values,
        condition_evaluation)

    all_false = False
    if action.conditions.filter(is_filter=False).count():
        # If there are conditions, check if they are all false
        all_false = all(
            not bool_val for __, bool_val in condition_evaluation.items()
        )

    # Evaluate the action content.
    show_values = ''
    incorrect_json = False
    if action.is_out:
        action_content = evaluate_row_action_out(action, eval_context)
        if action.action_type == models.Action.PERSONALIZED_JSON:
            incorrect_json = not _check_json_is_correct(action_content)
    else:
        action_content = _evaluate_row_action_in(action, eval_context)
    if action_content is None:
        action_content = _(
            'Error while retrieving content (index: {0})',
        ).format(idx)
    else:
        # Get the conditions used in the action content
        act_cond = action.get_used_conditions()
        # Get the variables/columns from the conditions
        act_vars = set().union(*[
            cond.columns.all()
            for cond in action.conditions.filter(name__in=act_cond)])

        act_vars = act_vars.union({
            triplet.column
            for triplet in action.column_condition_pair.all()})

        # Sort the variables/columns  by position and get the name
        show_values = ', '.join([
            '"{0}" = {1}'.format(col.name, row_values[col.name])
            for col in act_vars])

    uses_plain_text = (
        action.action_type == models.Action.PERSONALIZED_CANVAS_EMAIL
        or action.action_type == models.Action.PERSONALIZED_JSON
    )
    if uses_plain_text:
        action_content = escape(action_content)

    if prelude:
        prelude = evaluate_row_action_out(action, eval_context, prelude)

    # Update the context
    context.update({
        'n_items': n_items,
        'nxt': nxt,
        'prv': prv,
        'incorrect_json': incorrect_json,
        'show_values': show_values,
        'show_conditions': ', '.join(['"{0}" = {1}'.format(
            cond_name, str(cond_value))
            for cond_name, cond_value in condition_evaluation.items()]),
        'all_false': all_false,
        'prelude': prelude,
        'action_content': action_content,
        'show_navigation': True})


def create_list_preview_context(
    action: models.Action,
    context: Dict,
):
    """Create the elements to render a single row preview.

    :param action: Action being previewed.
    :param context: Dictionary to render the page
    :return: context is modified to include the appropriate items
    """
    # Obtain the evaluation context (no condition evaluation)
    action_final_text = evaluate_row_action_out(
        action,
        get_action_evaluation_context(action, {}))
    context['action_content'] = action_final_text
    if action.action_type == models.Action.JSON_REPORT:
        incorrect_json = not _check_json_is_correct(action_final_text)
        context['incorrect_json'] = incorrect_json
