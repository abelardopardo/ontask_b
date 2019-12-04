# -*- coding: utf-8 -*-

"""Task to upload/merge data in a workflow."""
import datetime

from celery import shared_task
from django.conf import settings
from django.utils.translation import ugettext
import pytz

from ontask import models
from ontask.core import services
from ontask.dataops.services.dataframeupload import (
    batch_load_df_from_athenaconnection,
)
from ontask.logs.services import get_log_item


@shared_task
def athena_dataupload_task(user_id, workflow_id, conn_id, params, log_id):
    """Upload or merge data using an Athena connection.

    :param user_id: Id of User object that is executing the action
    :param workflow_id: Workflow to upload the data
    :param conn_id: Athena connection ID
    :param params: Dictionary with additional parameters or the operation
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing, the result is stored in the log with log_id
    """
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return

    try:
        user, workflow, __ = services.get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id)

        conn = models.AthenaConnection.objects.filter(
            enabled=True).filter(pk=conn_id).first()
        if not conn:
            raise Exception(
                ugettext('Unable to find connection with id {0}').format(
                    conn_id))

        batch_load_df_from_athenaconnection(
            workflow,
            conn,
            params,
            log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.payload['datetime'] = str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = ugettext('Error: {0}').format(e)
        log_item.save()

    return
