# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

from datetime import datetime
from typing import List, Tuple

import pytz
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from ontask.action.payloads import (
    CanvasEmailPayload, EmailPayload, JSONPayload, SendListPayload,
)
from ontask.models import Action, Log, ScheduledAction
from ontask.tasks.basic import logger, run_task

cache_lock_format = '__ontask_scheduled_item_{0}'


def _update_item_status(
    s_item: ScheduledAction,
    run_result: List[str],
    debug: bool,
):
    """Update the status of the scheduled item.

    :param s_item: Scheduled item

    :return: Nothing
    """
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    if run_result is None:
        s_item.status = ScheduledAction.STATUS_DONE_ERROR
    else:
        if s_item.execute_until and s_item.execute_until > now:
            # There is a second date/time and is not passed yet!
            s_item.status = ScheduledAction.STATUS_PENDING
            # Update exclude values
            s_item.exclude_values.extend(run_result)
        else:
            s_item.status = ScheduledAction.STATUS_DONE

    # Save the new status in the DB
    s_item.save()

    if debug:
        logger.info('Status set to %s', s_item.status)


def _get_pending_items():
    """Fetch the actions pending execution.

    :return: QuerySet with the pending actions.
    """
    # Get the current date/time
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    # Get all the actions that are pending
    s_items = ScheduledAction.objects.filter(
        status=ScheduledAction.STATUS_PENDING,
        execute__lt=now)
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
    log_item = s_item.action.log(
        s_item.user,
        Log.ACTION_RUN_EMAIL,
        **action_info)
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
    log_item = s_item.action.log(
        s_item.user,
        Log.ACTION_RUN_SEND_LIST,
        **action_info)
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
    log_item = s_item.action.log(
        s_item.user,
        Log.ACTION_RUN_JSON,
        **action_info)
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
    log_item = s_item.action.log(
        s_item.user,
        Log.ACTION_RUN_JSON_LIST,
        **action_info)
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
    log_item = s_item.action.log(
        s_item.user,
        Log.ACTION_RUN_CANVAS_EMAIL,
        **action_info)
    return action_info, log_item


_function_distributor = {
    Action.PERSONALIZED_TEXT: _prepare_personalized_text,
    Action.SEND_LIST: _prepare_send_list,
    Action.PERSONALIZED_JSON: _prepare_personalized_json,
    Action.SEND_LIST_JSON: _prepare_send_list_json,
    Action.PERSONALIZED_CANVAS_EMAIL: _prepare_canvas_email}


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

        with cache.lock(cache_lock_format.format(s_item.id)):
            # Item is now locked by the cache mechanism
            s_item.refresh_from_db()
            if s_item.status != ScheduledAction.STATUS_PENDING:
                continue

            try:
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

                _update_item_status(s_item, run_result, debug)
            except Exception as exc:
                logger.error(
                    'Error while processing scheduled action: {0}'.format(
                        str(exc)))
