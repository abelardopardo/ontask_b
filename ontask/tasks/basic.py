# -*- coding: utf-8 -*-

"""Wrappers around asynchronous task executions."""

import datetime
from typing import Dict, List, Optional, Tuple

import pytz
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext

from ontask.action.send import (
    send_canvas_emails, send_emails, send_json, send_json_list,
    send_list_email,
)
from ontask.core.celery import get_task_logger
from ontask.models import Action, Log, Workflow

logger = get_task_logger('celery_execution')


def get_log_item(log_id: int) -> Optional[Log]:
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
            ugettext('Incorrect execution request with log_id %s'),
            str(log_id))

    return log_item


def get_execution_items(
    user_id: int,
    workflow_id: Optional[int] = None,
    action_id: Optional[int] = None,
) -> Tuple:
    """Get the objects with the given ids.

    Given a set of ids, get the objects from the DB

    :param user_id: User id

    :param workflow_id: Workflow ID (being manipulated)

    :param action_id: Action id (to be executed)

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
                    workflow_id))

    action = None
    if action_id:
        # Get the action
        action = Action.objects.filter(
            workflow__user=user,
            pk=action_id).first()
        if not action:
            raise Exception(
                ugettext('Unable to find action with id {0}').format(
                    action_id))

    return user, workflow, action


@shared_task
def run_task(
    user_id: int,
    log_id: int,
    action_info: Dict,
) -> Optional[List]:
    """Run the given task."""
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return None

    items_processed = None
    try:
        user, __, action = get_execution_items(
            user_id=user_id,
            action_id=action_info['action_id'])

        # Update the last_execution_log
        action.last_executed_log = log_item
        action.save()

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        if action.action_type == Action.PERSONALIZED_TEXT:
            items_processed = send_emails(user, action, action_info, log_item)
        elif action.action_type == Action.SEND_LIST:
            items_processed = send_list_email(
                user,
                action,
                action_info,
                log_item)
        elif action.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
            items_processed = send_canvas_emails(
                user,
                action,
                action_info,
                log_item)
        elif action.action_type == Action.PERSONALIZED_JSON:
            items_processed = send_json(
                user,
                action,
                action_info,
                log_item)
        elif action.action_type == Action.SEND_LIST_JSON:
            items_processed = send_json_list(
                user,
                action,
                action_info,
                log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.payload['objects_sent'] = len(items_processed)
        log_item.payload['filter_present'] = action.get_filter() is not None
        log_item.payload['datetime'] = str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
        log_item.save()
    except Exception as exc:
        log_item.payload['status'] = ugettext('Error: {0}').format(exc)
        log_item.save()

    return items_processed
