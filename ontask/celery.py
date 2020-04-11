# -*- coding: utf-8 -*-

"""Celery definitions and a test function."""
import os

from celery import Celery
from celery.task.control import inspect
from celery.utils.log import get_task_logger
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')

app = Celery('ontask')

LOGGER = get_task_logger('celery_execution')

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['ontask.tasks'])


@app.task(bind=True)
def debug_task(self):
    """Test celery execution."""
    if settings.DEBUG:
        LOGGER.debug('Celery running in development mode.')
    else:
        LOGGER.debug('Celery running in production mode.')

    LOGGER.debug('Request: %s', str(self.request))


def celery_is_up() -> bool:
    """Check if celery is up.

    :return: Boolean encoding if the process is running
    """
    if settings.CELERY_TASK_ALWAYS_EAGER:
        # Always running
        return True

    # Verify that celery is running!
    try:
        inspect().stats()
    except Exception:
        return False

    return True
