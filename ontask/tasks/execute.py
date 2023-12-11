"""Execute any operation received through celery."""
from typing import Dict, Optional, Tuple

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.utils.translation import gettext

from ontask import models
from ontask.tasks.execute_factory import TASK_EXECUTE_FACTORY

CELERY_LOGGER = get_task_logger('celery_execution')


def _get_execution_items(
    user_id: int,
    workflow_id: Optional[int] = None,
    action_id: Optional[int] = None,
) -> Tuple:
    """Get the objects with the given ids.

    Given a set of ids, get the objects from the DB

    :param user_id: User id
    :param workflow_id: Workflow ID (being manipulated)
    :param action_id: Action id (to be executed)
    :return: (user, action, log)
    """
    # Get the user
    user = None
    if user_id:
        user = get_user_model().objects.filter(id=user_id).first()
        if not user:
            raise Exception(
                gettext('Unable to find user with id {0}').format(user_id),
            )

    workflow = None
    if workflow_id:
        workflow = models.Workflow.objects.filter(
            user=user,
            pk=workflow_id).first()
        if not workflow:
            raise Exception(
                gettext('Unable to find workflow with id {0}').format(
                    workflow_id))

    action = None
    if action_id:
        # Get the action
        action = models.Action.objects.filter(
            workflow__user=user,
            pk=action_id).first()
        if not action:
            raise Exception(
                gettext('Unable to find action with id {0}').format(
                    action_id))

    return user, workflow, action


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
    try:
        user, workflow, action = _get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id,
            action_id=action_id)

        if log_id:
            log_item = models.Log.objects.get(pk=log_id)
            log_item.workflow = workflow
            log_item.payload['status'] = 'Executing'
            log_item.save(update_fields=['payload', 'workflow'])

        TASK_EXECUTE_FACTORY.execute_operation(user=user, workflow=workflow,
                                               action=action, payload=payload,
                                               log_item=log_item)

    except Exception as exc:
        if log_item is not None:
            log_item.payload['status'] = 'Error'
            log_item.save(update_fields=['payload'])

        CELERY_LOGGER.error(
            gettext('Error executing operation: {0}').format(exc))
        return

    if log_item:
        log_item.payload['status'] = 'Finished'
        log_item.save(update_fields=['payload'])
