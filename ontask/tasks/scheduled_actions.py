# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

from datetime import datetime, timedelta
from typing import Tuple

import pytz
from celery import shared_task
from django.conf import settings

from ontask.action.payloads import (
    CanvasEmailPayload, EmailPayload, JSONPayload, SendListPayload,
)
from ontask.models import Action, Log, ScheduledAction
from ontask.tasks.basic import logger, run_task


def _get_pending_items():
    """Fetch the actions pending execution.

    :return: QuerySet with the pending actions.
    """
    # Get the current date/time
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    # Get all the actions that are pending
    s_items = ScheduledAction.objects.filter(
        status=ScheduledAction.STATUS_PENDING,
        execute__lt=now + timedelta(minutes=1))
    logger.info('%s actions pending execution', s_items.count())

    return s_items


def _prepare_personalized_text(
    s_item: ScheduledAction,
) -> Tuple[EmailPayload, Log]:
    """Creaete Action info and log object for the Personalized email.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (EmailPlayload, Log item)
    """
    action_info = EmailPayload(s_item.payload)
    action_info['action_id'] = s_item.action_id
    action_info['item_column'] = s_item.item_column.name
    action_info['exclude_values'] = s_item.exclude_values

    # Log the event
    log_item = Log.objects.register(
        s_item.user,
        Log.SCHEDULE_EMAIL_EXECUTE,
        s_item.action.workflow,
        {
            'action': s_item.action.name,
            'action_id': s_item.action.id,
            'bcc_email': s_item.payload.get('bcc_email'),
            'cc_email': s_item.payload.get('cc_email'),
            'item_column': s_item.item_column.name,
            'execute': s_item.execute.isoformat(),
            'exclude_values': s_item.exclude_values,
            'from_email': s_item.user.email,
            'send_confirmation': s_item.payload.get(
                'send_confirmation'),
            'status': 'Preparing to execute',
            'subject': s_item.payload.get('subject'),
            'track_read': s_item.payload.get('track_read')})

    return action_info, log_item


def _prepare_send_list(
    s_item: ScheduledAction,
) -> Tuple[SendListPayload, Log]:
    """Create Action info and log object for the List email.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SendListPayload, Log item)
    """
    action_info = SendListPayload(s_item.payload)
    action_info['action_id'] = s_item.action_id

    # Log the event
    log_item = Log.objects.register(
        s_item.user,
        Log.SCHEDULE_SEND_LIST_EXECUTE,
        s_item.action.workflow,
        {
            'action': s_item.action.name,
            'action_id': s_item.action.id,
            'from_email': s_item.user.email,
            'email_to': s_item.payload.get('email_to'),
            'subject': s_item.payload.get('subject'),
            'bcc_email': s_item.payload.get('bcc_email'),
            'cc_email': s_item.payload.get('cc_email'),
            'execute': s_item.execute.isoformat(),
            'status': 'Preparing to execute'})

    return action_info, log_item


def _prepare_personalized_json(
    s_item: ScheduledAction,
) -> Tuple[JSONPayload, Log]:
    """Create Action info and log object for the Personalized JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (JSONPayload, Log item)
    """
    # Get the information about the keycolum
    item_column = None
    if s_item.item_column:
        item_column = s_item.item_column.name

    action_info = JSONPayload(s_item.payload)
    action_info['action_id'] = s_item.action_id
    action_info['item_column'] = item_column
    action_info['exclude_values'] = s_item.exclude_values

    # Log the event
    log_item = Log.objects.register(
        s_item.user,
        Log.SCHEDULE_JSON_EXECUTE,
        s_item.action.workflow,
        {
            'action': s_item.action.name,
            'action_id': s_item.action.id,
            'exclude_values': s_item.exclude_values,
            'item_column': item_column,
            'status': 'Preparing to execute',
            'target_url': s_item.action.target_url})

    return action_info, log_item


def _prepare_send_list_json(
    s_item: ScheduledAction,
) -> Tuple[JSONPayload, Log]:
    """Create Action info and log object for the List JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SendListPayload, Log item)
    """
    action_info = JSONPayload(s_item.payload)
    action_info['action_id'] = s_item.action_id

    # Log the event
    log_item = Log.objects.register(
        s_item.user,
        Log.SCHEDULE_JSON_EXECUTE,
        s_item.action.workflow,
        {
            'action': s_item.action.name,
            'action_id': s_item.action.id,
            'status': 'Preparing to execute',
            'target_url': s_item.action.target_url})

    return action_info, log_item


def _prepare_canvas_email(
    s_item: ScheduledAction,
) -> Tuple[CanvasEmailPayload, Log]:
    """Create Action info and log object for the List JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (CanvasEmailPayload, Log item)
    """
    # Get the information from the payload
    action_info = CanvasEmailPayload(s_item.payload)
    action_info['action_id'] = s_item.action_id
    action_info['item_column'] = s_item.item_column.name
    action_info['exclude_values'] = s_item.exclude_values

    # Log the event
    log_item = Log.objects.register(
        s_item.user,
        Log.SCHEDULE_EMAIL_EXECUTE,
        s_item.action.workflow,
        {
            'action': s_item.action.name,
            'action_id': s_item.action.id,
            'item_column': s_item.item_column.name,
            'execute': s_item.execute.isoformat(),
            'exclude_values': s_item.exclude_values,
            'from_email': s_item.user.email,
            'status': 'Preparing to execute',
            'subject': s_item.payload.get('subject', '')})

    return action_info, log_item


_function_distributor = {
    Action.personalized_text: _prepare_personalized_text,
    Action.send_list: _prepare_send_list,
    Action.personalized_json: _prepare_personalized_json,
    Action.send_list_json: _prepare_send_list_json,
    Action.personalized_canvas_email: _prepare_canvas_email}


@shared_task
def execute_scheduled_actions_task(debug: bool):
    """Execute the entries in the DB that are due.

    :return: Nothing.
    """
    # Get the current date/time
    s_items = _get_pending_items()

    # If the number of tasks to execute is zero, we are done.
    if s_items.count() == 0:
        return

    for s_item in s_items:
        if debug:
            logger.info('Starting execution of task %s', str(s_item.id))

        # Set item to running
        s_item.status = ScheduledAction.STATUS_EXECUTING
        s_item.save()

        run_result = None
        log_item = None
        action_info = None

        # Get action info and log item
        if s_item.action.action_type in _function_distributor:
            action_info, log_item = _function_distributor[
                s_item.action.action_type](s_item)

        if log_item:
            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())
            s_item.last_executed_log = log_item
        else:
            logger.error(
                'Execution of action type "%s" not implemented',
                s_item.action.action_type)

        if run_result:
            s_item.status = ScheduledAction.STATUS_DONE
        else:
            s_item.status = ScheduledAction.STATUS_DONE_ERROR
        # Save the new status in the DB
        s_item.save()

        if debug:
            logger.info('Status set to %s', s_item.status)
