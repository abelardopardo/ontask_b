# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

from datetime import datetime
from typing import List, Tuple

import pytz
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache

from ontask import core, models
from ontask.action.services.task import run

cache_lock_format = '__ontask_scheduled_item_{0}'
logger = get_task_logger('celery_execution')


def _update_item_status(
    s_item: models.ScheduledOperation,
    run_result: List[str],
    debug: bool,
):
    """Update the status of the scheduled item.

    :param s_item: Scheduled item

    :return: Nothing
    """
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    if run_result is None:
        s_item.status = models.scheduler.STATUS_DONE_ERROR
    else:
        if s_item.execute_until and s_item.execute_until > now:
            # There is a second date/time and is not passed yet!
            s_item.status = models.scheduler.STATUS_PENDING
            # Update exclude values
            s_item.exclude_values.extend(run_result)
        else:
            s_item.status = models.scheduler.STATUS_DONE

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
    s_items = models.ScheduledOperation.objects.filter(
        status=models.scheduler.STATUS_PENDING,
        execute__lt=now)
    logger.info('%s actions pending execution', s_items.count())

    return s_items


def _prepare_personalized_text(
    s_item: models.ScheduledOperation,
) -> Tuple[core.SessionPayload, models.Log]:
    """Create Action info and log object for the Personalized email.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SessionPayload, Log item)
    """
    payload = core.SessionPayload(s_item.payload)
    payload['action_id'] = s_item.action_id
    payload['item_column'] = s_item.item_column.name
    payload['exclude_values'] = s_item.exclude_values
    log_item = s_item.action.log(
        s_item.user,
        models.Log.ACTION_RUN_EMAIL,
        **payload)
    return payload, log_item


def _prepare_send_list(
    s_item: models.ScheduledOperation,
) -> Tuple[core.SessionPayload, models.Log]:
    """Create Action info and log object for the List email.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SendListPayload, Log item)
    """
    payload = core.SessionPayload(s_item.payload)
    payload['action_id'] = s_item.action_id
    log_item = s_item.action.log(
        s_item.user,
        models.Log.ACTION_RUN_SEND_LIST,
        **payload)
    return payload, log_item


def _prepare_personalized_json(
    s_item: models.ScheduledOperation,
) -> Tuple[core.SessionPayload, models.Log]:
    """Create Action info and log object for the Personalized JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (JSONPayload, Log item)
    """
    # Get the information about the keycolum
    item_column = None
    if s_item.item_column:
        item_column = s_item.item_column.name

    payload = core.SessionPayload(s_item.payload)
    payload['action_id'] = s_item.action_id
    payload['item_column'] = item_column
    payload['exclude_values'] = s_item.exclude_values

    # Log the event
    log_item = s_item.action.log(
        s_item.user,
        models.Log.ACTION_RUN_JSON,
        **payload)
    return payload, log_item


def _prepare_send_list_json(
    s_item: models.ScheduledOperation,
) -> Tuple[core.SessionPayload, models.Log]:
    """Create Action info and log object for the List JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SendListPayload, Log item)
    """
    payload = core.SessionPayload(s_item.payload)
    payload['action_id'] = s_item.action_id

    # Log the event
    log_item = s_item.action.log(
        s_item.user,
        models.Log.ACTION_RUN_JSON_LIST,
        **payload)
    return payload, log_item


def _prepare_canvas_email(
    s_item: models.ScheduledOperation,
) -> Tuple[core.SessionPayload, models.Log]:
    """Create Action info and log object for the List JSON.

    :param s_item: Scheduled Action item in the DB
    :return: Pair (SessionPayload, Log item)
    """
    # Get the information from the payload
    payload = core.SessionPayload(s_item.payload)
    payload['action_id'] = s_item.action_id
    payload['item_column'] = s_item.item_column.name
    payload['exclude_values'] = s_item.exclude_values
    log_item = s_item.action.log(
        s_item.user,
        models.Log.ACTION_RUN_CANVAS_EMAIL,
        **payload)
    return payload, log_item


_function_distributor = {
    models.Action.PERSONALIZED_TEXT: _prepare_personalized_text,
    models.Action.SEND_LIST: _prepare_send_list,
    models.Action.PERSONALIZED_JSON: _prepare_personalized_json,
    models.Action.SEND_LIST_JSON: _prepare_send_list_json,
    models.Action.PERSONALIZED_CANVAS_EMAIL: _prepare_canvas_email}


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
            if s_item.status != models.scheduler.STATUS_PENDING:
                continue

            try:
                # Set item to running
                s_item.status = models.scheduler.STATUS_EXECUTING
                s_item.save()

                run_result = None
                log_item = None
                action_info = None

                # Get action info and log item
                if s_item.action.action_type in _function_distributor:
                    action_info, log_item = _function_distributor[
                        s_item.action.action_type](s_item)

                if log_item:
                    run_result = run(
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
