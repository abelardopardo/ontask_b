"""Celery definitions and a test function."""
import os
import celery
from celery.signals import setup_logging  # noqa
from celery.utils.log import get_task_logger
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')

app = celery.Celery('ontask')

LOGGER = get_task_logger('celery_execution')

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['ontask.tasks'])


@setup_logging.connect
def on_celery_setup_logging(**kwargs):
    from logging.config import dictConfig  # noqa
    from django.conf import settings  # noqa

    dictConfig(settings.LOGGING)


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
        app.control.inspect().stats()
    except Exception:
        return False

    return True
