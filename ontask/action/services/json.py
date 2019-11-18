# -*- coding: utf-8 -*-

"""Views to run JSON actions."""
import datetime
import json
from typing import Dict, Mapping, Optional, List

import pytz
import requests
from celery.utils.log import get_task_logger
from django.conf import settings

from ontask import OnTaskSharedState, models, tasks
from ontask.action import forms
from ontask.action.evaluate import (
    evaluate_action, evaluate_row_action_out, get_action_evaluation_context,
)
from ontask.action.services.manager import ActionManagerBase
from ontask.action.services.manager_factory import action_run_request_factory

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


class ActionManagerJSON(ActionManagerBase):
    """Class to serve running an email action."""

    def __init__(self):
        """Assign default fields."""
        super().__init__(
            forms.JSONActionRunForm,
            models.Log.ACTION_RUN_JSON)
        self.template = 'action/request_json_data.html'

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ) -> Optional[List]:
        """Send the personalized JSON objects to the given URL."""
        if log_item is None:
            log_item = action.log(user, self.log_event, **payload)

        action_evals = evaluate_action(
            action,
            column_name=action.workflow.columns.get(
                pk=payload['item_column']).name,
            exclude_values=payload.get('exclude_values'),
        )

        # Create the headers to use for all requests
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(payload['token']),
        }

        # Iterate over all json objects to create the strings and check for
        # correctness
        for json_string, _ in action_evals:
            _send_and_log_json(
                user,
                action,
                json.loads(json_string),
                headers)

        action.last_executed_log = log_item
        action.save()

        return [column_value for __, column_value in action_evals]


class ActionManagerJSONList(ActionManagerBase):
    """Class to serve running an email action."""

    def __init__(self):
        """Assign default fields."""
        super().__init__(
            forms.JSONListActionRunForm,
            models.Log.ACTION_RUN_JSON_LIST)
        self.template = 'action/request_json_list_data.html'

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ) -> Optional[List]:
        """Send single json object to target URL.

        Sends a single json object to the URL in the action

        :param user: User object that executed the action

        :param action: Action from where to take the messages

        :param log_item: Log object to store results

        :param payload: Object with the additional parameters

        :return: Empty list (there are no column values for multiple sends)
        """
        if log_item is None:
            action.log(user, self.log_event, **payload)

        action_text = evaluate_row_action_out(
            action,
            get_action_evaluation_context(action, {}))

        _send_and_log_json(
            user,
            action,
            json.loads(action_text),
            {
                'content-type': 'application/x-www-form-urlencoded; '
                + 'charset=UTF-8',
                'Authorization': 'Bearer {0}'.format(payload['token']),
            })

        action.last_executed_log = log_item
        action.save()

        return []


process_obj = ActionManagerJSON()
process_list = ActionManagerJSONList()
action_run_request_factory.register_producer(
    models.Action.PERSONALIZED_JSON,
    process_obj)
action_run_request_factory.register_producer(
    models.Action.JSON_LIST,
    process_list)

tasks.task_execute_factory.register_producer(
    models.Action.PERSONALIZED_JSON,
    process_obj)
tasks.task_execute_factory.register_producer(
    models.Action.JSON_LIST,
    process_list)
