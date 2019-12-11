# -*- coding: utf-8 -*-

"""Execute any operation received through celery."""
from typing import Any, Dict, Optional

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.translation import ugettext

from ontask import models
from ontask.core import services

CELERY_LOGGER = get_task_logger('celery_execution')


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

    def execute_operation(self, operation_type, **kwargs) -> Any:
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
        :return: Whatever is returned by the execution
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
    run_result = None
    try:
        user, workflow, action = services.get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id,
            action_id=action_id)

        log_item = None
        if log_id:
            log_item = models.Log.objects.get(pk=log_id)
            log_item.payload['status'] = 'Executing'
            log_item.save()

        task_execute_factory.execute_operation(
            operation_type=operation_type,
            user=user,
            workflow=workflow,
            action=action,
            payload=payload,
            log_item=log_item)

    except Exception as exc:
        CELERY_LOGGER.error(
            ugettext('Error executing operation: {0}').format(exc))
