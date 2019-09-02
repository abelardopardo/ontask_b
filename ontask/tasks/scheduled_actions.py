# -*- coding: utf-8 -*-

"""Process the scheduled actions."""

from datetime import datetime, timedelta

import pytz
from celery import shared_task
from django.conf import settings

from ontask.action.payloads import (
    CanvasEmailPayload, EmailPayload, JSONPayload, SendListPayload,
)
from ontask.models import Action, Log, ScheduledAction
from ontask.tasks.basic import logger, run_task


@shared_task
def execute_scheduled_actions_task(debug: bool):
    """Execute the entries in the DB that are due.

    :return: Nothing.
    """
    # Get the current date/time
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    # Get all the actions that are pending
    s_items = ScheduledAction.objects.filter(
        status=ScheduledAction.STATUS_PENDING,
        execute__lt=now + timedelta(minutes=1))
    logger.info('{0} actions pending execution', s_items.count())

    # If the number of tasks to execute is zero, we are done.
    if s_items.count() == 0:
        return

    for s_item in s_items:
        if debug:
            logger.info('Starting execution of task {0}', str(s_item.id))

        # Set item to running
        s_item.status = ScheduledAction.STATUS_EXECUTING
        s_item.save()

        run_result = None
        log_item = None
        #
        # EMAIL ACTION
        #
        if s_item.action.action_type == Action.personalized_text:
            action_info = EmailPayload(s_item.payload)
            action_info['action_id'] = s_item.action_id
            action_info['item_column'] = s_item.item_column.name
            action_info['exclude_values'] = s_item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                s_item.user,
                Log.SCHEDULE_EMAIL_EXECUTE,
                s_item.action.workflow,
                {
                    'action': s_item.action.name,
                    'action_id': s_item.action.id,
                    'bcc_email': s_item.payload.get('bcc_email'),
                    'cc_email': s_item.payload.get('cc_email'),
                    'item_column': s_item.item_column.name,
                    'execute': s_item.execute.isoformat(),
                    'exclude_values': s_item.exclude_values,
                    'from_email': s_item.user.email,
                    'send_confirmation': s_item.payload.get(
                        'send_confirmation'),
                    'status': 'Preparing to execute',
                    'subject': s_item.payload.get('subject'),
                    'track_read': s_item.payload.get('track_read')})

            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())

        #
        # SEND LIST ACTION
        #
        elif s_item.action.action_type == Action.send_list:
            action_info = SendListPayload(s_item.payload)
            action_info['action_id'] = s_item.action_id

            # Log the event
            log_item = Log.objects.register(
                s_item.user,
                Log.SCHEDULE_SEND_LIST_EXECUTE,
                s_item.action.workflow,
                {
                    'action': s_item.action.name,
                    'action_id': s_item.action.id,
                    'from_email': s_item.user.email,
                    'email_to': s_item.payload.get('email_to'),
                    'subject': s_item.payload.get('subject'),
                    'bcc_email': s_item.payload.get('bcc_email'),
                    'cc_email': s_item.payload.get('cc_email'),
                    'execute': s_item.execute.isoformat(),
                    'status': 'Preparing to execute'})

            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())

        #
        # JSON action
        #
        elif s_item.action.action_type == Action.personalized_json:
            # Get the information about the keycolum
            item_column = None
            if s_item.item_column:
                item_column = s_item.item_column.name

            action_info = JSONPayload(s_item.payload)
            action_info['action_id'] = s_item.action_id
            action_info['item_column'] = item_column
            action_info['exclude_values'] = s_item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                s_item.user,
                Log.SCHEDULE_JSON_EXECUTE,
                s_item.action.workflow,
                {
                    'action': s_item.action.name,
                    'action_id': s_item.action.id,
                    'exclude_values': s_item.exclude_values,
                    'item_column': item_column,
                    'status': 'Preparing to execute',
                    'target_url': s_item.action.target_url})

            # Send the objects
            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())

        #
        # JSON LIST action
        #
        elif s_item.action.action_type == Action.send_list_json:
            # Get the information about the keycolum
            item_column = None
            if s_item.item_column:
                item_column = s_item.item_column.name

            action_info = JSONPayload(s_item.payload)
            action_info['action_id'] = s_item.action_id

            # Log the event
            log_item = Log.objects.register(
                s_item.user,
                Log.SCHEDULE_JSON_EXECUTE,
                s_item.action.workflow,
                {
                    'action': s_item.action.name,
                    'action_id': s_item.action.id,
                    'status': 'Preparing to execute',
                    'target_url': s_item.action.target_url})

            # Send the objects
            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())

        #
        # Canvas Email Action
        #
        elif s_item.action.action_type == Action.personalized_canvas_email:
            # Get the information from the payload
            action_info = CanvasEmailPayload(s_item.payload)
            action_info['action_id'] = s_item.action_id
            action_info['item_column'] = s_item.item_column.name
            action_info['exclude_values'] = s_item.exclude_values

            # Log the event
            log_item = Log.objects.register(
                s_item.user,
                Log.SCHEDULE_EMAIL_EXECUTE,
                s_item.action.workflow,
                {
                    'action': s_item.action.name,
                    'action_id': s_item.action.id,
                    'item_column': s_item.item_column.name,
                    'execute': s_item.execute.isoformat(),
                    'exclude_values': s_item.exclude_values,
                    'from_email': s_item.user.email,
                    'status': 'Preparing to execute',
                    'subject': s_item.payload.get('subject', '')})

            run_result = run_task(
                s_item.user.id,
                log_item.id,
                action_info.get_store())
        else:
            logger.error(
                'Execution of action type "{0}" not implemented',
                s_item.action.action_type)

        if run_result:
            s_item.status = ScheduledAction.STATUS_DONE
        else:
            s_item.status = ScheduledAction.STATUS_DONE_ERROR

        if debug:
            logger.info('Status set to {0}', s_item.status)

        if log_item:
            # Store the log event in the scheduling item
            s_item.last_executed_log = log_item

        # Save the new status in the DB
        s_item.save()
