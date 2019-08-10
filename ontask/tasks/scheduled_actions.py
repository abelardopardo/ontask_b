# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

import datetime
from datetime import datetime, timedelta

import pytz
from celery import shared_task
from django.conf import settings as ontask_settings

from ontask.action.models import Action
from ontask.action.payloads import (
    EmailPayload, JSONPayload, CanvasEmailPayload
)
from ontask.logs.models import Log
from ontask.scheduler.models import ScheduledAction
from ontask.tasks.basic import logger
from ontask.tasks.send_canvas_email import send_canvas_email_messages
from ontask.tasks.send_email import send_email_messages
from ontask.tasks.send_json import send_json_objects


@shared_task
def execute_scheduled_actions(debug: bool):
    """
    Function that selects the entries in the DB that are due, and proceed with
    the execution.

    :return:
    """
    # Get the current date/time
    now = datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))

    # Get all the actions that are pending
    s_items = ScheduledAction.objects.filter(
        status=ScheduledAction.STATUS_PENDING,
        execute__lt=now + timedelta(minutes=1)
    )
    logger.info('{0} actions pending execution'.format(s_items.count()))

    # If the number of tasks to execute is zero, we are done.
    if s_items.count() == 0:
        return

    for item in s_items:
        if debug:
            logger.info('Starting execution of task ' + str(item.id))

        # Set item to running
        item.status = ScheduledAction.STATUS_EXECUTING
        item.save()

        result = None

        #
        # EMAIL ACTION
        #
        if item.action.action_type == Action.personalized_text:
            action_info = EmailPayload(item.payload)
            action_info['action_id'] = item.action_id
            action_info['item_column'] = item.item_column.name
            action_info['exclude_values'] = item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                item.user,
                Log.SCHEDULE_EMAIL_EXECUTE,
                item.action.workflow,
                {
                    'action': item.action.name,
                    'action_id': item.action.id,
                    'bcc_email': item.payload.get('bcc_email'),
                    'cc_email': item.payload.get('cc_email'),
                    'email_column': item.item_column.name,
                    'execute': item.execute.isoformat(),
                    'exclude_values': item.exclude_values,
                    'from_email': item.user.email,
                    'send_confirmation': item.payload.get('send_confirmation'),
                    'status': 'Preparing to execute',
                    'subject': item.payload.get('subject'),
                    'track_read': item.payload.get('track_read'),
                }
            )

            result = send_email_messages(
                item.user.id,
                log_item.id,
                action_info.get_store()
            )

        #
        # JSON action
        #
        elif item.action.action_type == Action.personalized_json:
            # Get the information about the keycolum
            key_column = None
            if item.item_column:
                key_column = item.item_column.name

            action_info = JSONPayload(item.payload)
            action_info['action_id'] = item.action_id
            action_info['item_column'] = key_column
            action_info['exclude_values'] = item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                item.user,
                Log.SCHEDULE_JSON_EXECUTE,
                item.action.workflow,
                {
                    'action': item.action.name,
                    'action_id': item.action.id,
                    'exclude_values': item.exclude_values,
                    'key_column': key_column,
                    'status': 'Preparing to execute',
                    'target_url': item.action.target_url})

            # Send the objects
            result = send_json_objects(
                item.user.id,
                log_item.id,
                action_info.get_store()
            )

        #
        # Canvas Email Action
        #
        elif item.action.action_type == Action.personalized_canvas_email:
            # Get the information from the payload
            action_info = CanvasEmailPayload(item.payload)
            action_info['action_id'] = item.action_id
            action_info['item_column'] = item.item_column.name
            action_info['exclude_values'] = item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                item.user,
                Log.SCHEDULE_EMAIL_EXECUTE,
                item.action.workflow,
                {
                    'action': item.action.name,
                    'action_id': item.action.id,
                    'email_column': item.item_column.name,
                    'execute': item.execute.isoformat(),
                    'exclude_values': item.exclude_values,
                    'from_email': item.user.email,
                    'status': 'Preparing to execute',
                    'subject': item.payload.get('subject', ''),
                }
            )

            result = send_canvas_email_messages(
                item.user.id,
                log_item.id,
                action_info.get_store()
            )

        if result:
            item.status = ScheduledAction.STATUS_DONE
        else:
            item.status = ScheduledAction.STATUS_DONE_ERROR

        if debug:
            logger.info('Status set to {0}'.format(item.status))

        # Store the log event in the scheduling item
        item.last_executed_log = log_item

        # Save the new status in the DB
        item.save()
