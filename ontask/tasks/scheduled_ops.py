# -*- coding: utf-8 -*-

"""Process the scheduled actions."""
from datetime import datetime
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
import pytz

from ontask import CELERY_LOGGER, models
from ontask.tasks.execute import task_execute_factory

cache_lock_format = '__ontask_scheduled_item_{0}'


def _update_item_status(
    s_item: models.ScheduledOperation,
    run_result: List[str],
):
    """Update the status of the scheduled item.

    :param s_item: Scheduled item
    :return: Nothing
    """
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    if run_result is None:
        s_item.status = models.scheduler.STATUS_DONE_ERROR
    else:
        if s_item.frequency and (
            not s_item.execute_until or now < s_item.execute_until
        ):
            # There is a future execution
            s_item.status = models.scheduler.STATUS_PENDING
            # Update exclude values
            s_item.exclude_values.extend(run_result)
        else:
            s_item.status = models.scheduler.STATUS_DONE

    # Save the new status in the DB
    s_item.save()

    if settings.DEBUG:
        CELERY_LOGGER.info('Status set to %s', s_item.status)


@shared_task
def execute_scheduled_operation(s_item_id: int):
    """Execute the scheduled operation in s_item."""

    s_item = models.ScheduledOperation.objects.filter(pk=s_item_id).first()
    if not s_item:
        if settings.DEBUG:
            CELERY_LOGGER.info('Operation without scheduled item.')
        return

    with cache.lock(cache_lock_format.format(s_item.id)):
        # Item is now locked by the cache mechanism
        s_item.refresh_from_db()
        if s_item.status != models.scheduler.STATUS_PENDING:
            if settings.DEBUG:
                CELERY_LOGGER.info(
                    'Operation with status {0}.'.format(s_item.status))
            return

        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        if s_item.execute and now < s_item.execute:
            # Not yet
            if settings.DEBUG:
                CELERY_LOGGER.info('Too soon to execute operation.')
            return

        if s_item.execute_until and now > s_item.execute_until:
            # Too late
            if settings.DEBUG:
                CELERY_LOGGER.info('Too late to execute operation.')
            return

        if settings.DEBUG:
            CELERY_LOGGER.info('EXECUTING execute_scheduled_operation')

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

            _update_item_status(s_item, run_result)
        except Exception as exc:
            CELERY_LOGGER.error(
                'Error while processing scheduled action: {0}'.format(
                    str(exc)))
