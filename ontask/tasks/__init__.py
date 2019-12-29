# -*- coding: utf-8 -*-

"""Import packages and initialize the task_execute_factory."""
from django.conf import settings
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from ontask.tasks.execute_factory import (
    execute_operation, task_execute_factory,
)
from ontask.tasks.scheduled_ops import execute_scheduled_operation
from ontask.tasks.session_cleanup import session_cleanup

CLEAN_SESSION_TASK_NAME = '__ONTASK_CLEANUP_SESSION_TASK'
CRONTAB_ITEMS = settings.SESSION_CLEANUP_CRONTAB.split()
SCHEDULE, _ = CrontabSchedule.objects.get_or_create(
    minute=CRONTAB_ITEMS[0],
    hour=CRONTAB_ITEMS[1],
    day_of_week=CRONTAB_ITEMS[2],
    day_of_month=CRONTAB_ITEMS[3],
    month_of_year=CRONTAB_ITEMS[4])

CLEAN_SESSION_TASK = PeriodicTask.objects.filter(
    name=CLEAN_SESSION_TASK_NAME).first()
if not CLEAN_SESSION_TASK:
    PeriodicTask.objects.create(
        crontab=SCHEDULE,
        name=CLEAN_SESSION_TASK_NAME,
        task='ontask.tasks.session_cleanup.session_cleanup')
