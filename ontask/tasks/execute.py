# -*- coding: utf-8 -*-

"""Execute any operation received through celery."""
import datetime
from typing import Dict, Optional

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils.translation import ugettext
import pytz

from ontask.core.services import get_execution_items
from ontask.logs.services import get_log_item

LOGGER = get_task_logger('celery_execution')


class ExecuteFactory:
    """Factory to execute all received operations."""

    def __init__(self):
        """Initialize the set of _creators."""
        self._producers = {}

    def register_producer(self, operation_type: str, producer_obj):
        """Register the given object that will process the operation type."""
        if operation_type in self._producers:
            raise ValueError(operation_type)
        self._producers[operation_type] = producer_obj

    def execute_operation(self, operation_type, **kwargs):
        """Execute the given operation.

        Invoke the object that implements the following method
        def execute_operation(
            self,
            user,
            workflow: Optional[models.Workflow] = None,
            action: Optional[models.Action] = None,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
        ):

        :param operation_type: String encoding the type of operation
        :param kwargs: Parameters passed to execution
        :return: Nothing
        """
        producer_obj = self._producers.get(operation_type)
        if not producer_obj:
            raise ValueError(operation_type)
        return producer_obj.execute_operation(**kwargs)


task_execute_factory = ExecuteFactory()


@shared_task
def execute_operation(
    operation_type: str,
    user_id: Optional[int] = None,
    log_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    action_id: Optional[int] = None,
    payload: Optional[Dict] = None,
):
    """Execute the operation.

    :param operation_type: Type of operation to execute.
    :param user_id: User id.
    :param log_id: log id.
    :param workflow_id: workflow id (if needed).
    :param action_id: Action id (if needed).
    :param payload: Rest of parameters.
    :return: Nothing
    """
    log_item = None
    if log_id:
        log_item = get_log_item(log_id)
        if not log_item:
            return None

    try:
        user, workflow, action = get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id,
            action_id=action_id)

        # Set the status to "executing" before calling the function
        if log_item:
            log_item.payload['status'] = 'Executing'
            log_item.save()

        run_result = task_execute_factory.execute_operation(
            operation_type=operation_type,
            user=user,
            workflow=workflow,
            action=action,
            payload=payload,
            log_item=log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.payload['datetime'] = str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
        log_item.payload['run_result'] = run_result
        log_item.save()

    except Exception as exc:
        log_item.payload['status'] = ugettext('Error: {0}').format(exc)
        log_item.save()
