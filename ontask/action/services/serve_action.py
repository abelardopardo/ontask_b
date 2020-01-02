# -*- coding: utf-8 -*-

"""Functions to serve actions through direct URL access."""
import json
import random
from typing import Any, Dict, List, Tuple

from django import http
from django.http.request import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.action.evaluate import (
    evaluate_row_action_out,
    get_action_evaluation_context, get_row_values,
)
from ontask.action.services.errors import (
    OnTaskActionSurveyDataNotFound,
    OnTaskActionSurveyNoTableData,
)
from ontask.dataops import sql


def serve_action_out(
    user,
    action: models.Action,
    user_attribute_name: str,
):
    """Serve request for an action out.

    Function that given a user and an Action Out
    searches for the appropriate data in the table with the given
    attribute name equal to the user email and returns the HTTP response.
    :param user: User object making the request
    :param action: Action to execute (action out)
    :param user_attribute_name: Column to check for email
    :return:
    """
    # User_instance has the record used for verification
    row_values = get_row_values(action, (user_attribute_name, user.email))

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(action, row_values)
    if context is None:
        # Log the event
        action.log(
            user,
            models.Log.ACTION_SERVED_EXECUTE,
            error=_('Error when evaluating conditions for user {0}').format(
                user.email))

        return http.HttpResponse(render_to_string(
            'action/action_unavailable.html',
            {}))

    # Evaluate the action content.
    action_content = evaluate_row_action_out(action, context)

    # If the action content is empty, forget about it
    response = action_content
    if action_content is None:
        response = render_to_string('action/action_unavailable.html', {})

    # Log the event
    action.log(
        user,
        models.Log.ACTION_SERVED_EXECUTE,
        error=_('Error when evaluating conditions for user {0}').format(
            user.email))

    # Respond the whole thing
    return http.HttpResponse(response)


def get_survey_context(
    request: http.HttpRequest,
    is_manager: bool,
    action: models.Action,
    user_attribute_name: str,
) -> Dict:
    """Get the context to render a survey page.

    :param request: Request received
    :param is_manager: User is manager
    :param action: Action object being executed
    :param user_attribute_name: Name of the column to use for username
    :return: Dictionary with the context
    """
    # Get the attribute value depending if the user is managing the workflow
    # User is instructor, and either owns the workflow or is allowed to access
    # it as shared
    user_attribute_value = None
    if is_manager:
        user_attribute_value = request.GET.get('uatv')
    if not user_attribute_value:
        user_attribute_value = request.user.email

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(
        action,
        get_row_values(
            action,
            (user_attribute_name, user_attribute_value),
        ),
    )

    if not context:
        # If the data has not been found, flag
        if not is_manager:
            raise OnTaskActionSurveyDataNotFound()

        raise OnTaskActionSurveyNoTableData(
            message=_('Data not found in the table'))

    return context


def update_row_values(
    request: HttpRequest,
    action: models.Action,
    row_data: Tuple[List, List, str, Any],
):
    """Serve a request for action in.

    Function that given a request, and an action IN, it performs the lookup
     and data input of values.

    :param request: HTTP request
    :param action:  Action In
    :param row_data: Tuple containing keys, values, where_field, where_value.
    Keys and values are the values in the row. Where field, and where value is
    pair find the given row
    :return:
    """
    keys, values, where_field, where_value = row_data
    # Execute the query
    sql.update_row(
        action.workflow.get_data_frame_table_name(),
        keys,
        values,
        filter_dict={where_field: where_value},
    )

    # Recompute all the values of the conditions in each of the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for act in action.workflow.actions.all():
        act.update_n_rows_selected()

    # Log the event and update its content in the action
    log_item = action.log(
        request.user,
        models.Log.ACTION_SURVEY_INPUT,
        new_values=json.dumps(dict(zip(keys, values))))

    # Modify the time of execution for the action
    action.last_executed_log = log_item
    action.save(update_fields=['last_executed_log'])


def extract_survey_questions(
    action: models.Action, user_seed: str,
) -> List[models.ActionColumnConditionTuple]:
    """Extract the set of questions to include in a survey.

    :param action: Action being executed
    :param user_seed: Seed so that it can be replicated several times and
    is user dependent
    :return: List of ColumnCondition pairs
    """
    # Get the active columns attached to the action
    colcon_items = [
        pair for pair in action.column_condition_pair.all()
        if pair.column.is_active
    ]

    if action.shuffle:
        # Shuffle the columns if needed
        random.seed(user_seed)
        random.shuffle(colcon_items)

    return colcon_items
