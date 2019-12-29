# -*- coding: utf-8 -*-

"""Import packages and initialize the task_execute_factory."""
from django.conf import settings
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from ontask.tasks.execute_factory import (
    execute_operation, task_execute_factory,
)
from ontask.tasks.scheduled_ops import execute_scheduled_operation
from ontask.tasks.session_cleanup import session_cleanup

clean_session_task_name = '__ONTASK_CLEANUP_SESSION_TASK'
crontab_items = settings.SESSION_CLEANUP_CRONTAB.split()
schedule, _ = CrontabSchedule.objects.get_or_create(
    minute=crontab_items[0],
    hour=crontab_items[1],
    day_of_week=crontab_items[2],
    day_of_month=crontab_items[3],
    month_of_year=crontab_items[4])

clean_session_task = PeriodicTask.objects.filter(
    name=clean_session_task_name).first()
if not clean_session_task:
    PeriodicTask.objects.create(
        crontab=schedule,
        name=clean_session_task_name,
        task='ontask.tasks.session_cleanup.session_cleanup')
