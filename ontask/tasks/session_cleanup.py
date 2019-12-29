# -*- coding: utf-8 -*-

"""Cleaning the session table."""

from celery import shared_task
from django.core import management


@shared_task
def session_cleanup():
    """Cleanup expired sessions using pre-defined command."""
    management.call_command("clearsessions", verbosity=0)
