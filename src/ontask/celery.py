# -*- coding: utf-8 -*-

"""Celery definitions and a test function."""

import os

from celery import Celery
from celery.task.control import inspect
from celery.utils.log import get_task_logger
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'ontask.settings.production')

app = Celery('ontask')

logger = get_task_logger('celery_execution')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['ontask'])


@app.task(bind=True)
def debug_task(self):
    """Test celery execution."""
    if settings.DEBUG:
        logger.debug('Celery running in development mode.')
    else:
        logger.debug('Celery running in production mode.')

    logger.debug('Request: {info}', extras={'info': self.request})


def celery_is_up():
    """Check if celery is up.

    :return: Boolean encoding if the process is running
    """
    # Verify that celery is running!
    try:
        inspect().stats()
    except Exception:
        return False

    return True
