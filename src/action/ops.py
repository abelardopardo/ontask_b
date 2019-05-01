# -*- coding: utf-8 -*-

"""Auxiliary operations to handle actions.

File with auxiliary operations needed to handle the actions, namely:
functions to process request when receiving a "serve" action, cloning
operations when cloning conditions and actions, and sending messages.
"""

from builtins import str
from typing import Tuple, Union

from celery.utils.log import get_task_logger
from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from action.evaluate_action import (
    action_evaluation_context,
    evaluate_row_action_out, get_row_values,
)
from action.models import Action, ActionColumnConditionTuple, Condition
from logs.models import Log
from workflow.models import Workflow
from workflow.ops import get_workflow

logger = get_task_logger('celery_execution')


def serve_action_out(
    user,
    action: Action,
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
    # For the response
    payload = {
        'action': action.name,
        'action_id': action.id,
    }

    # User_instance has the record used for verification
    row_values = get_row_values(
        action,
        (user_attribute_name, user.email),
    )

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = action_evaluation_context(action, row_values)
    if context is None:
        payload['error'] = (
            _('Error when evaluating conditions for user {0}').format(
                user.email,
            )
        )
        # Log the event
        Log.objects.register(
            user,
            Log.ACTION_SERVED_EXECUTE,
            workflow=action.workflow,
            payload=payload)
        return HttpResponse(render_to_string(
            'action/action_unavailable.html',
            {}))

    # Evaluate the action content.
    action_content = evaluate_row_action_out(action, context)

    # If the action content is empty, forget about it
    response = action_content
    if action_content is None:
        response = render_to_string('action/action_unavailable.html', {})
        payload['error'] = _('Action not enabled for user {0}').format(
            user.email,
        )

    # Log the event
    Log.objects.register(
        user,
        Log.ACTION_SERVED_EXECUTE,
        workflow=action.workflow,
        payload=payload)

    # Respond the whole thing
    return HttpResponse(response)


def clone_condition(
    condition: Condition,
    new_action: Action = None,
    new_name: str = None,
):
    """Clone a condition.

    Function to clone a condition and change action and/or name
    :param condition: Condition to clone
    :param new_action: New action to point
    :param new_name: New name
    :return: New condition
    """
    condition.id = None
    if new_action:
        condition.action = new_action
    if new_name:
        condition.name = new_name
    condition.save()

    return condition


def clone_action(
    action: Action,
    new_workflow: Workflow = None,
    new_name: str = None,
):
    """Clone an action.

    Function that given an action clones it and changes workflow and name
    :param action: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """
    # Store the old object id before squashing it
    old_id = action.id

    # Clone
    action.id = None

    # Update some of the fields
    if new_name:
        action.name = new_name
    if new_workflow:
        action.workflow = new_workflow

    # Update
    action.save()

    # Get back the old action
    old_action = Action.objects.prefetch_related(
        'column_condition_pair', 'conditions',
    ).get(id=old_id)

    # Clone the columns field (in case of an action in).
    if action.is_in:
        action.column_condition_pair.delete()
        for acc_tuple in old_action.column_condition_pair.all():
            __, __ = ActionColumnConditionTuple.objects.get_or_create(
                action=action,
                column=acc_tuple.column,
                condition=acc_tuple.condition,
            )

    # Clone the conditions
    for condition in old_action.conditions.all():
        clone_condition(condition, action)

    # Update
    action.save()

    return action


def get_workflow_action(
    request: HttpRequest,
    pk: int,
) -> Union[Tuple[None, None], Tuple[Workflow, Action]]:
    """Get workflow and action for the session.

    Function that returns the action for the given PK and the workflow for
    the session.

    :param request:
    :param pk: Action id.
    :return: (workflow, Action) or None
    """
    # Get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return None, None

    if workflow.nrows == 0:
        messages.error(
            request,
            'Workflow has no data. Go to "Manage table data" to upload data.',
        )
        return None, None

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).prefetch_related(
        'column_condition_pair',
    ).first()
    if not action:
        return None, None

    return workflow, action


