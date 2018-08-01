# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from action.models import Action
from action.ops import send_messages
from logs.models import Log

logger = get_task_logger(__name__)


@shared_task
def send_email_messages(user_id,
                        action_id,
                        subject,
                        email_column,
                        from_email,
                        cc_email_list,
                        bcc_email_list,
                        send_confirmation,
                        track_read,
                        log_id):
    """
    This function invokes send_messages in action/ops.py, gets the message
    that may be sent as a result, and records the appropriate events.

    :param user_id: Id of User object that is executing the action
    :param action: Action object from where the messages are taken
    :param subject: String for the email subject
    :param email_column: Name of the column to extract email addresses
    :param from_email: String with email from sender
    :param cc_email_list: List of CC emails
    :param bcc_email_list: List of BCC emails
    :param send_confirmation: Boolean to send confirmation to sender
    :param track_read: Boolean to try to track reads
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing
    """

    # Get the objects
    user = get_user_model().objects.get(id=user_id)
    action = Action.objects.get(id=action_id)

    # Get the log_item to modify the message
    log_item = Log.objects.get(pk=log_id)
    payload = log_item.get_payload()
    payload['status'] = 'Executing'
    log_item.set_payload(payload)
    log_item.save()

    msg = 'Finished'
    try:
        result = send_messages(user,
                               action,
                               subject,
                               email_column,
                               from_email,
                               cc_email_list,
                               bcc_email_list,
                               send_confirmation,
                               track_read)
        # If the result has some sort of message, push it to the log
        if result:
            msg = 'Incorrect execution: ' + str(result)
            logger.error(msg)

    except Exception as e:
        msg = 'Error while executing send_messages: {0}'.format(e.message)
        logger.error(msg)
    else:
        logger.info(msg)

    # Update the message in the payload
    payload['status'] = msg
    log_item.set_payload(payload)
    log_item.save()
