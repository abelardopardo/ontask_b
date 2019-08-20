from celery import shared_task
from django.utils.translation import ugettext

from ontask.action.payloads import JSONPayload
from ontask.action.send import send_json
from ontask.models import Log
from ontask.tasks.basic import get_execution_items, get_log_item


@shared_task
def send_json_objects(
    user_id: int,
    log_id: Log,
    action_info: JSONPayload,
) -> bool:
    """Invokes send_json in action

    Gets the JSON objects that may be sent as a result, and records the
    appropriate events.

    :param user_id: Id of User object that is executing the action
    :param action_id: Id of Action object from where the messages are taken
    :param token: String to include as authorisation token
    :param key_column: Key column name to use to exclude elements (if needed)
    :param exclude_values: List of values to exclude from the mailing
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing
    """
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user, __, action = get_execution_items(
            user_id=user_id,
            action_id=action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        send_json(user, action, log_item, action_info)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        to_return = False

    return to_return
