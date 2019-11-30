# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

from datetime import datetime
from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
import pytz

from ontask import models
from ontask.tasks.execute import task_execute_factory

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


@shared_task
def execute_scheduled_operations_task(debug: bool):
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

                payload = s_item.payload
                if s_item.item_column:
                    payload['item_column'] = s_item.item_column.pk
                if s_item.exclude_values is not None:
                    payload['exclude_values'] = s_item.exclude_values

                run_result = task_execute_factory.execute_operation(
                    operation_type=s_item.operation_type,
                    user=s_item.user,
                    workflow=s_item.workflow,
                    action=s_item.action,
                    payload=payload)

                _update_item_status(s_item, run_result, debug)
            except Exception as exc:
                logger.error(
                    'Error while processing scheduled action: {0}'.format(
                        str(exc)))
