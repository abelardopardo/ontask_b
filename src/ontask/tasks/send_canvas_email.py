from celery import shared_task
from django.utils.translation import ugettext

from action.payloads import CanvasEmailPayload
from action.send import send_canvas_emails
from ontask.tasks.basic import get_log_item, get_execution_items


@shared_task
def send_canvas_email_messages(
    user_id: int,
    log_id: int,
    action_info: CanvasEmailPayload
) -> bool:
    """
    This function invokes send_messages in action, gets the message
    that may be sent as a result, and records the appropriate events.

    :param user_id: Id of User object that is executing the action
    :param action_id: Id of Action object from where the messages are taken
    :param subject: String for the email subject
    :param email_column: Name of the column to extract email addresses
    :param exclude_values: List of values to exclude from the mailing
    :param target_url: The name of the server to use to send email
    :param log_id: Id of the log object where the status has to be reflected
    :return: bool stating if execution has been correct
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    try:
        user, __, action = get_execution_items(
            user_id=user_id,
            action_id=action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        send_canvas_emails(
            user,
            action,
            log_item,
            action_info,
        )

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()

        return False

    return True
