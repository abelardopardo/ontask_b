# -*- coding: utf-8 -*-

"""Send personalized emails using Canvas API."""
import datetime
import json
from time import sleep
from typing import Dict, Mapping, Tuple

import pytz
import requests
from celery.utils.log import get_task_logger
from django.conf import settings as ontask_settings
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import status

from action.evaluate.action import evaluate_action
from action.models import Action
from logs.models import Log
from ontask_oauth.models import OnTaskOAuthUserTokens
from ontask_oauth.views import refresh_token

logger = get_task_logger('celery_execution')


def send_canvas_emails(
    user,
    action: Action,
    log_item: Log,
    action_info: Mapping,
):
    """Send CANVAS emails with the action content evaluated for each row.

    Performs the submission of the emails for the given action and with the
    given subject. The subject will be evaluated also with respect to the
    rows, attributes, and conditions.
    :param user: User object that executed the action
    :param action: Action from where to take the messages
    :param log_item: Log object to store results
    :param action_info: Mapping key, value as defined in CanvasEmailPayload
    :return: Send the emails
    """
    # Evaluate the action string, evaluate the subject, and get the value of
    # the email column.
    action_evals = evaluate_action(
        action,
        extra_string=action_info['subject'],
        column_name=action_info['item_column'],
        exclude_values=action_info['exclude_values'])

    # Get the oauth info
    target_url = action_info['target_url']
    oauth_info = ontask_settings.CANVAS_INFO_DICT.get(target_url)
    if not oauth_info:
        raise Exception(_('Unable to find OAuth Information Record'))

    # Get the token
    user_token = OnTaskOAuthUserTokens.objects.filter(
        user=user,
        instance_name=target_url,
    ).first()
    if not user_token:
        # There is no token, execution cannot proceed
        raise Exception(_('Incorrect execution due to absence of token'))

    # Create the headers to use for all requests
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': 'Bearer {0}'.format(user_token.access_token),
    }

    # Create the context for the log events
    context = {
        'user': user.id,
        'action': action.id,
    }

    # Send the objects to the given URL
    idx = 1
    burst = oauth_info['aux_params'].get('burst')
    burst_pause = oauth_info['aux_params'].get('pause', 0)
    domain = oauth_info['domain_port']
    conversation_url = oauth_info['conversation_url'].format(domain)
    for msg_body, msg_subject, msg_to in action_evals:
        #
        # JSON object to send. Taken from method.conversations.create in
        # https://canvas.instructure.com/doc/api/conversations.html
        #
        canvas_email_payload = {
            'recipients[]': msg_to,
            'body': msg_body,
            'subject': msg_subject,
        }

        # Manage the bursts
        do_burst_pause(burst, burst_pause, idx)
        # Index to detect bursts
        idx += 1

        # Send the email
        if ontask_settings.EXECUTE_ACTION_JSON_TRANSFER:
            result_msg, response_status = send_single_canvas_message(
                target_url,
                conversation_url,
                canvas_email_payload,
                headers,
                oauth_info,
            )
        else:
            # Print the JSON that would be sent through the logger
            logger.info(
                'SEND JSON({target}): {obj}',
                extra={
                    'target': target_url,
                    'obj': json.dumps(canvas_email_payload),
                },
            )
            result_msg = 'SENT TO LOGGER'
            response_status = 200

        # Log message sent
        context['object'] = json.dumps(canvas_email_payload)
        context['status'] = response_status
        context['result'] = result_msg
        context['email_sent_datetime'] = str(
            datetime.datetime.now(pytz.timezone(ontask_settings.TIME_ZONE)),
        )
        Log.objects.register(
            user,
            Log.ACTION_CANVAS_EMAIL_SENT,
            action.workflow,
            context)

    # Update data in the overall log item
    log_item.payload['objects_sent'] = len(action_evals)
    log_item.payload['filter_present'] = action.get_filter() is not None
    log_item.payload['datetime'] = str(datetime.datetime.now(pytz.timezone(
        ontask_settings.TIME_ZONE)))
    log_item.save()

    return None


def refresh_and_retry_send(
    target_url,
    oauth_info,
    conversation_url,
    canvas_email_payload,
):
    """Refresh OAuth token and retry send.

    :return:
    """
    # Request rejected due to token expiration. Refresh the
    # token
    user_token = None
    result_msg = ugettext('OAuth token refreshed')
    try:
        user_token = refresh_token(user_token, oauth_info)
    except Exception as exc:
        result_msg = str(exc)

    if user_token:
        # Update the header with the new token
        headers = {
            'content-type':
                'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(
                user_token.access_token,
            ),
        }

        # Second attempt at executing the API call
        response = requests.post(
            url=conversation_url,
            data=canvas_email_payload,
            headers=headers)
        response_status = response.status_code

    return result_msg, response_status


def do_burst_pause(burst: int, burst_pause: int, idx: int):
    """Detect end of burst and pause if needed.

    :param burst: Burst length
    :param burst_pause: Pause after length is reached
    :param idx: Current index
    :return:
    """
    if burst and (idx % burst) == 0:
        # Burst exists and the limit has been reached
        logger.info(
            'Burst ({burst}) reached. Waiting for {pause} secs',
            extra={'burst': burst, 'pause': burst_pause},
        )
        sleep(burst_pause)


def send_single_canvas_message(
    target_url: str,
    conversation_url: str,
    canvas_email_payload,
    headers: Dict,
    oauth_info,
) -> Tuple[str, int]:
    """Send a single email to Canvas using the API.

    :param target_url: Target URL in the canvas server
    :param conversation_url: URL pointing to the conversation object
    :param canvas_email_payload: Email message
    :param headers: HTTP headers for the request
    :param oauth_info: Authentication info
    :return: response message, response status
    """
    result_msg = ugettext('Message successfuly sent')

    # Send the email through the API call
    # First attempt
    response = requests.post(
        url=conversation_url,
        data=canvas_email_payload,
        headers=headers)
    response_status = response.status_code

    req_rejected = (
        response.status_code == status.HTTP_401_UNAUTHORIZED
        and response.headers.get('WWW-Authenticate')
    )
    if req_rejected:
        result_msg, response_status = refresh_and_retry_send(
            target_url,
            oauth_info,
            conversation_url,
            canvas_email_payload,
        )
    elif response_status != status.HTTP_201_CREATED:
        result_msg = ugettext(
            'Unable to deliver message (code {0})').format(
            response_status)

    return result_msg, response_status
