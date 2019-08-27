# -*- coding: utf-8 -*-

"""Wrappers around asynchronous task executions."""

from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext

from ontask.core.celery import get_task_logger
from ontask.models import Action, Log, Workflow

logger = get_task_logger('celery_execution')


def get_log_item(log_id):
    """Get the log object.

    Given a log_id, fetch it from the Logs table. This is the object used to
    write all the diagnostics.

    :param log_id: PK of the Log object to get
    :return:
    """
    log_item = Log.objects.filter(pk=log_id).first()
    if not log_item:
        # Not much can be done here. Call has no place to report error...
        logger.error(
            ugettext('Incorrect execution request with log_id {lid}'),
            extras={'lid': log_id},
        )

    return log_item


def get_execution_items(
    user_id: int,
    workflow_id: Optional[int] = None,
    action_id: Optional[int] = None,
) -> Tuple:
    """Get the objects with the given ids.

    Given a set of ids, get the objects from the DB

    :param user_id: User id

    :param action_id: Action id (to be executed)

    :param log_id: Log id (to store execution report)

    :return: (user, action, log)
    """
    # Get the user
    user = get_user_model().objects.get(id=user_id)
    if not user:
        raise Exception(
            ugettext('Unable to find user with id {0}').format(user_id),
        )

    workflow = None
    if workflow_id:
        workflow = Workflow.objects.filter(user=user, pk=workflow_id).first()
        if not workflow:
            raise Exception(
                ugettext('Unable to find workflow with id {0}').format(
                    workflow_id,
                ),
            )

    action = None
    if action_id:
        # Get the action
        action = Action.objects.filter(
            workflow__user=user,
            pk=action_id).first()
        if not action:
            raise Exception(
                ugettext('Unable to find action with id {0}').format(
                    action_id,
                ),
            )

    return user, workflow, action


def run_task(
    task_function: Callable[[Any, Action, Log, Dict], None],
    user_id: int,
    log_id: int,
    action_info: Mapping,
) -> bool:
    """"Run the given task."""
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    try:
        user, __, action = get_execution_items(
            user_id=user_id,
            action_id=action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        task_function(user, action, log_item, action_info)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        return False

    return True
