# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

import datetime
from datetime import datetime, timedelta

import pytz
from celery import shared_task
from django.conf import settings as ontask_settings

from ontask.apps.action.models import Action
from ontask.apps.logs.models import Log
from ontask.tasks.basic import logger
from ontask.tasks.send_canvas_email import send_canvas_email_messages
from ontask.tasks.send_email import send_email_messages
from ontask.tasks.send_json import send_json_objects
from ontask.apps.scheduler.models import ScheduledAction


@shared_task
def execute_scheduled_actions(debug):
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
            subject = item.payload.get('subject', '')
            cc_email = item.payload.get('cc_email', [])
            bcc_email = item.payload.get('bcc_email', [])
            send_confirmation = item.payload.get('send_confirmation', False)
            track_read = item.payload.get('track_read', False)

            # Log the event
            log_item = Log.objects.register(
                item.user,
                Log.SCHEDULE_EMAIL_EXECUTE,
                item.action.workflow,
                {
                    'action': item.action.name,
                    'action_id': item.action.id,
                    'bcc_email': bcc_email,
                    'cc_email': cc_email,
                    'email_column': item.item_column.name,
                    'execute': item.execute.isoformat(),
                    'exclude_values': item.exclude_values,
                    'from_email': item.user.email,
                    'send_confirmation': send_confirmation,
                    'status': 'Preparing to execute',
                    'subject': subject,
                    'track_read': track_read,
                }
            )

            # Store the log event in the scheduling item
            item.last_executed_log = log_item
            item.save()

            result = send_email_messages(
                item.user.id,
                item.action.id,
                subject,
                item.item_column.name,
                item.user.email,
                cc_email,
                bcc_email,
                send_confirmation,
                track_read,
                item.exclude_values,
                log_item.id)

        #
        # JSON action
        #
        elif item.action.action_type == Action.personalized_json:
            # Get the information from the payload
            token = item.payload['token']
            key_column = None
            if item.item_column:
                key_column = item.item_column.name

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
                item.action.id,
                token,
                key_column,
                item.exclude_values,
                log_item.id)
        #
        # Canvas Email Action
        #
        elif item.action.action_type == Action.personalized_canvas_email:
            # Get the information from the payload
            token = item.payload['token']
            subject = item.payload.get('subject', '')

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
                    'subject': subject,
                }
            )

            result = send_canvas_email_messages(
                item.user_id,
                item.action_id,
                subject,
                item.item_column_name,
                item.user.email,
                token,
                item.exclude_values,
                log_item.id)

        if result:
            item.status = ScheduledAction.STATUS_DONE
        else:
            item.status = ScheduledAction.STATUS_DONE_ERROR

        if debug:
            logger.info('Status set to {0}'.format(item.status))

        # Save the new status in the DB
        item.save()
