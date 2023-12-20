"""Common functions for services."""
from importlib import import_module
from typing import Dict

from django.conf import settings
from django.utils.translation import gettext_lazy as _

import ontask
from ontask import models
from ontask.core.session_ops import acquire_workflow_access

SESSION_STORE = import_module(settings.SESSION_ENGINE).SessionStore


def access_workflow(
        user,
        session,
        workflow_id: int,
        log_item: models.Log
) -> models.Workflow:
    """Acquire workflow access or raise exception."""
    workflow = acquire_workflow_access(user, session, workflow_id)
    if not workflow:
        msg = _('Unable to acquire access to workflow.')
        log_item.payload['error'] = msg
        log_item.save(update_fields=['payload'])
        raise ontask.OnTaskException(msg)


def create_session():
    # Create session
    session = SESSION_STORE()
    session.create()
    return session


def get_how_merge(payload: Dict, log_item: models.Log) -> str:
    how_merge = payload.get('how_merge')
    if not how_merge:
        msg = _('Missing merge method.')
        log_item.payload['error'] = msg
        log_item.save(update_fields=['payload'])
        raise ontask.OnTaskException(msg)
    return how_merge


def get_key(payload: Dict, key_name: str, log_item: models.Log) -> str:
    """Get the key name from payload."""
    key = payload.get(key_name)
    if not key:
        msg = _('Missing key name "{0}"'.format(key_name))
        log_item.payload['error'] = msg
        log_item.save(update_fields=['payload'])
        raise ontask.OnTaskException(msg)
    return key
