"""Process the scheduled actions."""
from datetime import datetime
from zoneinfo import ZoneInfo

from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from ontask import CELERY_LOGGER, models
from ontask.core import ONTASK_SCHEDULED_LOCKED_ITEM
from ontask.tasks import TASK_EXECUTE_FACTORY


def _update_item_status(s_item: models.ScheduledOperation):
    """Update the status of the scheduled item.

    :param s_item: Scheduled item
    :return: Nothing
    """
    now = datetime.now(ZoneInfo(settings.TIME_ZONE))
    if s_item.frequency and (
        not s_item.execute_until or now < s_item.execute_until
    ):
        new_status = models.scheduler.STATUS_PENDING
    else:
        new_status = models.scheduler.STATUS_DONE

    # Save the new status in the DB
    models.ScheduledOperation.objects.filter(pk=s_item.id).update(
        status=new_status)
    s_item.refresh_from_db(fields=['status'])

    if settings.DEBUG:
        CELERY_LOGGER.info('Status set to %s', s_item.status)


@shared_task
def execute_scheduled_operation(s_item_id: int):
    """Execute the scheduled operation in s_item.

    :param s_item_id: ID of the scheduled item to execute
    :return: Nothing, execution carries out normally.
    """

    s_item = models.ScheduledOperation.objects.filter(pk=s_item_id).first()
    if not s_item:
        if settings.DEBUG:
            CELERY_LOGGER.info('Operation without scheduled item.')
        return

    with cache.lock(ONTASK_SCHEDULED_LOCKED_ITEM.format(s_item.id)):
        # Item is now locked by the cache mechanism
        s_item.refresh_from_db()
        if s_item.status != models.scheduler.STATUS_PENDING:
            if settings.DEBUG:
                CELERY_LOGGER.info('Operation with status %s.', s_item.status)
            return

        now = datetime.now(ZoneInfo(settings.TIME_ZONE))
        if (
                s_item.execute_start and
                s_item.frequency and
                now < s_item.execute_start):
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
            models.ScheduledOperation.objects.filter(pk=s_item.id).update(
                status=models.scheduler.STATUS_EXECUTING)
            s_item.refresh_from_db(fields=['status'])

            # Create and update the log
            log_item = s_item.log(s_item.operation_type)
            s_item.last_executed_log = log_item
            s_item.save(update_fields=['last_executed_log'])

            payload = s_item.payload

            TASK_EXECUTE_FACTORY.execute_operation(
                operation_type=s_item.operation_type,
                user=s_item.user,
                workflow=s_item.workflow,
                action=s_item.action,
                payload=payload,
                log_item=log_item)

            # Update payload
            s_item.save()

            _update_item_status(s_item)
        except Exception as exc:
            msg = 'Error processing action {0}: {1}'.format(
                s_item.name,
                str(exc))
            CELERY_LOGGER.error(msg)
            log_item.payload['error'] = msg
            log_item.save()
            models.ScheduledOperation.objects.filter(pk=s_item.id).update(
                status=models.scheduler.STATUS_DONE_ERROR)
