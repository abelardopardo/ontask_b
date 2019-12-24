# -*- coding: utf-8 -*-

"""Function to manage celery tasks associated with the scheduled items.."""
import json

from django_celery_beat.models import (
    ClockedSchedule, CrontabSchedule, PeriodicTask)

from ontask import models
from ontask.core import ONTASK_SCHEDULED_TASK_NAME_TEMPLATE
from ontask.scheduler.services import errors


def delete_task(s_item: models.ScheduledOperation):
    """Delete the task corresponding to the given scheduled item.

    :param s_item: Scheduled operation item being processed.
    :return: Delete the task in the  PeriodicTask table
    """
    if s_item.task:
        s_item.task.delete()


def schedule_task(s_item: models.ScheduledOperation):
    """Create the task corresponding to the given scheduled item.

    :param s_item: Scheduled operation item being processed.
    :return: Creates a new task in the  PeriodicTask table

    If the s_item already contains a pointer to a task in PeriodicTasks, it
    is canceled.
    """
    delete_task(s_item)

    msg = s_item.are_times_valid()
    if msg:
        raise errors.OnTaskScheduleIncorrectTimes(msg)

    # Case of a single execution in the future
    if s_item.execute and not s_item.frequency and not s_item.execute_until:
        # Case 5
        clocked_item, __ = ClockedSchedule.objects.get_or_create(
            clocked_time=s_item.execute)
        task_id = PeriodicTask.objects.create(
            clocked=clocked_item,
            name=ONTASK_SCHEDULED_TASK_NAME_TEMPLATE.format(s_item.id),
            task='ontask.tasks.scheduled_ops.execute_scheduled_operation',
            args=json.dumps([s_item.id]))
    else:
        # Cases 3, 4, 7 and 8: crontab execution
        crontab_items = s_item.frequency.split()
        crontab_item, __ = CrontabSchedule.objects.get_or_create(
            minute=crontab_items[0],
            hour=crontab_items[1],
            day_of_week=crontab_items[2],
            day_of_month=crontab_items[3],
            month_of_year=crontab_items[4])

        task_id = PeriodicTask.objects.create(
            crontab=crontab_item,
            name=ONTASK_SCHEDULED_TASK_NAME_TEMPLATE.format(s_item.id),
            task='ontask.tasks.scheduled_ops.execute_scheduled_operation',
            args=json.dumps([s_item.id]))

    s_item.task = task_id
    s_item.save()
