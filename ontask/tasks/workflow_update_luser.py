# -*- coding: utf-8 -*-

"""Task to update the users connected to a workflow (luser field)."""

import logging
from typing import Dict, Optional

from django.utils.translation import ugettext

from ontask import models
from ontask.tasks.execute import task_execute_factory
from ontask.workflow.services.luser_update import do_workflow_update_lusers

logger = logging.getLogger('celery_execution')


class ExecuteUpdateWorkflowLUser:
    """Update the LUSER field in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.WORKFLOW_UPDATE_LUSERS

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """
        Recalculate the elements in field lusers of the workflow based on the
        fields luser_email_column and luser_email_column_MD5

        :param user: User object that is executing the action
        :param workflow: Workflow being processed (if applicable)
        :param action: Action being executed (if applicable)
        :param payload: Dictionary with the execution parameters
        :param log_id: Id of the log object where the status is reflected
        :return: Nothing, the result is stored in the log with log_id
        """
        if not log_item and self.log_event:
            log_item = workflow.log(
                user,
                operation_type=self.log_event,
                **payload)

        # First get the log item to make sure we can record diagnostics
        try:
            do_workflow_update_lusers(workflow, log_item)

            # Reflect status in the log event
            log_item.payload['status'] = 'Execution finished successfully'
            log_item.save()
        except Exception as e:
            log_item.payload['status'] = \
                ugettext('Error: {0}').format(e)
            log_item.save()


task_execute_factory.register_producer(
    models.Log.WORKFLOW_UPDATE_LUSERS,
    ExecuteUpdateWorkflowLUser())
