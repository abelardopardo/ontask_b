# -*- coding: utf-8 -*-

"""Views to run JSON actions."""
import datetime
import json
from typing import Mapping, Optional

from celery.utils.log import get_task_logger
from django.conf import settings
import pytz
import requests

from ontask import OnTaskSharedState, models
from ontask.action import forms
from ontask.action.evaluate import (
    evaluate_action, evaluate_row_action_out,
    get_action_evaluation_context,
)
from ontask.action.services.run_producer_base import ActionServiceRunBase

logger = get_task_logger('celery_execution')


def _send_and_log_json(
    user,
    action: models.Action,
    json_obj: str,
    headers: Mapping,
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
    action.log(
        user,
        models.Log.ACTION_JSON_SENT,
        object=json.dumps(json_obj),
        status=status_val,
        json_sent_datetime=str(datetime.datetime.now(pytz.timezone(
            settings.TIME_ZONE))))


def send_json(
    user,
    action: models.Action,
    action_info: Mapping,
    log_item: Optional[models.Log] = None,
):
    """Send json objects to target URL.

    Sends the json objects evaluated per row to the URL in the action

    :param user: User object that executed the action

    :param action: Action from where to take the messages

    :param log_item: Log object to store results

    :return: List of column values used to select the objects
    """
    # Evaluate the action string and obtain the list of list of JSON objects
    item_column = action.workflow.columns.get(pk=action_info['item_column'])
    action_evals = evaluate_action(
        action,
        column_name=item_column.name,
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
    for json_string, _ in action_evals:
        _send_and_log_json(
            user,
            action,
            json.loads(json_string),
            headers)

    return [column_value for _, column_value in action_evals]


def send_json_list(
    user,
    action: models.Action,
    action_info: Mapping,
    log_item: Optional[models.Log] = None,
):
    """Send single json object to target URL.

    Sends a single json object to the URL in the action

    :param user: User object that executed the action

    :param action: Action from where to take the messages

    :param log_item: Log object to store results

    :param action_info: Object with the additional parameters

    :return: Empty list (there are no column values for multiple sends)
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
        })

    return []

class ActionServiceRunJSON(ActionServiceRunBase):
    """Class to serive running an email action."""

    def __init__(self):
        """Assign """
        super().__init__(forms.JSONActionRunForm)
        self.template = 'action/request_json_data.html'
        self.log_event = models.Log.ACTION_RUN_JSON


class ActionServiceRunJSONList(ActionServiceRunBase):
    """Class to serive running an email action."""

    def __init__(self):
        """Assign """
        super().__init__(forms.JSONListActionRunForm)
        self.template = 'action/request_json_list_data.html'
        self.log_event = models.Log.ACTION_RUN_JSON_LIST
