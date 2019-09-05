# -*- coding: utf-8 -*-

"""Function to send JSON objects to target URL in action."""

import datetime
import json
from typing import Dict, Mapping

import pytz
import requests
from django.conf import settings

from ontask import OnTaskSharedState
from ontask.action.evaluate.action import (
    evaluate_action, evaluate_row_action_out, get_action_evaluation_context,
)
from ontask.core.celery import get_task_logger
from ontask.models import Action, Log

logger = get_task_logger('celery_execution')


def _send_and_log_json(
    user,
    action: Action,
    json_obj: str,
    headers: Mapping,
    context: Dict[str, str],
):
    """Send a JSON object to the action URL and LOG event."""
    if settings.EXECUTE_ACTION_JSON_TRANSFER:
        http_resp = requests.post(
            url=action.target_url,
            data=json_obj,
            headers=headers)
        status_val = http_resp.status_code
    else:
        payload = {
            'target': action.target_url,
            'text': json.dumps(json_obj),
            'auth': headers['Authorization']}
        logger.info('SEND JSON(%s): %s', action.target_url, payload['text'])
        if getattr(OnTaskSharedState, 'json_outbox', None):
            OnTaskSharedState.json_outbox.append(payload)
        else:
            OnTaskSharedState.json_outbox = [payload]
        status_val = 200

    # Log seng object
    context['object'] = json.dumps(json_obj)
    context['status'] = status_val
    context['json_sent_datetime'] = str(
        datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
    Log.objects.register(
        user,
        Log.ACTION_JSON_SENT,
        action.workflow,
        context)


def send_json(
    user,
    action: Action,
    log_item: Log,
    action_info: Mapping,
):
    """Send json objects to target URL.

    Sends the json objects evaluated per row to the URL in the action

    :param user: User object that executed the action

    :param action: Action from where to take the messages

    :param log_item: Log object to store results

    :return: Nothing
    """
    # Evaluate the action string and obtain the list of list of JSON objects
    action_evals = evaluate_action(
        action,
        column_name=action_info['item_column'],
        exclude_values=action_info['exclude_values'],
    )

    # Create the headers to use for all requests
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': 'Bearer {0}'.format(action_info['token']),
    }

    # Create the context for the log events
    context = {
        'user': user.id,
        'action': action.id,
    }

    # Iterate over all json objects to create the strings and check for
    # correctness
    for json_string in action_evals:
        _send_and_log_json(
            user,
            action,
            json.loads(json_string[0]),
            headers,
            context,
        )

        # Update data in the overall log item
    log_item.payload['objects_sent'] = len(action_evals)
    log_item.payload['filter_present'] = action.get_filter() is not None
    log_item.payload['datetime'] = str(
        datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
    log_item.save()


def send_json_list(
    user,
    action: Action,
    log_item: Log,
    action_info: Mapping,
):
    """Send single json object to target URL.

    Sends a single json object to the URL in the action

    :param user: User object that executed the action

    :param action: Action from where to take the messages

    :param log_item: Log object to store results

    :param action_info: Object with the additional parameters

    :return: Nothing
    """
    # Evaluate the action string and obtain the list of list of JSON objects
    action_text = evaluate_row_action_out(
        action,
        get_action_evaluation_context(action, {}))

    _send_and_log_json(
        user,
        action,
        json.loads(action_text),
        {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(action_info['token']),
        },
        {'user': user.id, 'action': action.id})

    # Update data in the overall log item
    log_item.payload['filter_present'] = action.get_filter() is not None
    log_item.payload['datetime'] = str(
        datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
    log_item.save()
