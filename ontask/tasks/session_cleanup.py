"""Cleaning the session table."""

from celery import shared_task
from django.core import management


@shared_task
def session_cleanup():
    """Cleanup expired sessions using pre-defined command.

    This function is not executed anywhere in the platform, but it is invoked
    regularly by the workers at a frequency determined in the configuration
    file.
    """
    management.call_command("clearsessions", verbosity=0)
