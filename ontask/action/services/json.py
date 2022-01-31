"""Functions to run JSON actions."""
import datetime
import json
from typing import Dict, Mapping, Optional

from celery.utils.log import get_task_logger
from django.conf import settings
import pytz
import requests

from ontask import OnTaskSharedState, models
from ontask.action.evaluate import (
    evaluate_action, evaluate_row_action_out, get_action_evaluation_context,
)
from ontask.action.services.run_factory import ActionRunProducerBase

LOGGER = get_task_logger('celery_execution')


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
        LOGGER.info('SEND JSON(%s): %s', action.target_url, payload['text'])
        if getattr(OnTaskSharedState, 'json_outbox', None):
            OnTaskSharedState.json_outbox.append(payload)
        else:
            OnTaskSharedState.json_outbox = [payload]
        status_val = 200

    # Log seng object
    action.log(
        user,
        models.Log.ACTION_JSON_SENT,
        action=action.id,
        object=json.dumps(json_obj),
        status=status_val,
        json_sent_datetime=str(datetime.datetime.now(pytz.timezone(
            settings.TIME_ZONE))))


class ActionRunProducerJSON(ActionRunProducerBase):
    """Class execute personalised JSON actions."""

    # Type of event to log when running the action
    log_event = models.Log.ACTION_RUN_PERSONALIZED_JSON

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Send the personalized JSON objects to the given URL."""
        if log_item is None:
            log_item = action.log(user, self.log_event, **payload)

        action_evaluations = evaluate_action(
            action,
            column_name=action.workflow.columns.get(
                pk=payload['item_column']).name,
            exclude_values=payload.get('exclude_values', []),
        )

        # Create the headers to use for all requests
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(payload['token']),
        }

        # Iterate over all json objects to create the strings and check for
        # correctness
        for json_string, _ in action_evaluations:
            _send_and_log_json(
                user,
                action,
                json.loads(json_string),
                headers)

        action.last_executed_log = log_item
        action.save(update_fields=['last_executed_log'])

        # Update excluded items in payload
        self._update_excluded_items(
            payload,
            [column_value for __, column_value in action_evaluations])


class ActionRunProducerJSONReport(ActionRunProducerBase):
    """Class to execute JSON report actions."""

    # Type of event to log when running the action
    log_event = models.Log.ACTION_RUN_JSON_REPORT

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Send single json object to target URL.

        Sends a single json object to the URL specified in the action.

        :param user: User executing the action
        :param workflow: Workflow object (if relevant)
        :param action: Action from where to take the messages
        :param payload: Object with the additional parameters
        :param log_item: Log object to store results
        :return: Empty list (there are no column values for multiple sends)
        """
        if log_item is None:
            action.log(user, self.log_event, action=action.id, **payload)

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
        action.save(update_fields=['last_executed_log'])
