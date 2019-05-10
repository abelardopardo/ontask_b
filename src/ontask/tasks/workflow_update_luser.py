from celery import shared_task
from django.utils.translation import ugettext

from ontask.tasks.basic import get_execution_items, get_log_item
from workflow.ops import do_workflow_update_lusers


@shared_task
def workflow_update_lusers(user_id, workflow_id, log_id):
    """
    Recalculate the elements in field lusers of the workflow based on the fields
    luser_email_column and luser_email_column_MD5

    :param user_id: Id of User object that is executing the action
    :param workflow_id: Id of workflow being processed
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing, the result is stored in the log with log_id
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user, workflow, __ = get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id)

        do_workflow_update_lusers(workflow, log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        to_return = False

    return to_return
