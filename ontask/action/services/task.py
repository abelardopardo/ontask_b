import datetime
from typing import Dict, List, Optional

import pytz
from celery import shared_task
from django.conf import settings
from django.utils.translation import ugettext

from ontask.action.services.manager_factory import action_run_request_factory
from ontask.core.services import get_execution_items
from ontask.logs.services import get_log_item


@shared_task
def run(user_id: int, log_id: int, payload: Dict) -> Optional[List]:
    """Run the given task."""
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return None

    items_processed = None
    try:
        user, workflow, action = get_execution_items(
            user_id=user_id,
            action_id=payload['action_id'])

        # Update the last_execution_log
        action.last_executed_log = log_item
        action.save()

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        items_processed = action_run_request_factory.process_run(
            payload.get('operation_type'),
            user=user,
            action=action,
            payload=payload,
            log_item=log_item)
        # if (
        #     action.action_type == Action.PERSONALIZED_TEXT
        #     or action.action_type == Action.RUBRIC_TEXT
        # ):
        #     items_processed = services.send_emails(
        #         user,
        #         action,
        #         payload,
        #         log_item)
        # elif action.action_type == Action.SEND_LIST:
        #     items_processed = services.send_list_email(
        #         user,
        #         action,
        #         payload,
        #         log_item)
        # elif action.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
        #     items_processed = send_canvas_emails(
        #         user,
        #         action,
        #         payload,
        #         log_item)
        # elif action.action_type == Action.PERSONALIZED_JSON:
        #     items_processed = send_json(
        #         user,
        #         action,
        #         payload,
        #         log_item)
        # elif action.action_type == Action.SEND_LIST_JSON:
        #     items_processed = send_json_list(
        #         user,
        #         action,
        #         payload,
        #         log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.payload['objects_sent'] = len(items_processed)
        log_item.payload['filter_present'] = action.get_filter() is not None
        log_item.payload['datetime'] = str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))
        log_item.save()
    except Exception as exc:
        log_item.payload['status'] = ugettext('Error: {0}').format(exc)
        log_item.save()

    return items_processed
