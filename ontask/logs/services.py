# -*- coding: utf-8 -*-

"""Service functions to manipulate logs."""

from typing import Optional

from django.utils.translation import ugettext

from ontask.core.celery import get_task_logger
from ontask.models import Log

logger = get_task_logger('celery_execution')


def get_log_item(log_id: int) -> Optional[Log]:
    """Get the log object.

    Given a log_id, fetch it from the Logs table. This is the object used to
    write all the diagnostics.

    :param log_id: PK of the Log object to get
    :return:
    """
    log_item = Log.objects.filter(pk=log_id).first()
    if not log_item:
        # Not much can be done here. Call has no place to report error...
        logger.error(
            ugettext('Incorrect execution request with log_id %s'),
            str(log_id))

    return log_item
