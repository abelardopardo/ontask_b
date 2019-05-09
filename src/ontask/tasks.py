# -*- coding: utf-8 -*-

"""Wrapper around task execution.

    TODO: Review the functions get_task_* and see if they can be implemented
    as decorators to take care of anomalies.
"""

import datetime
from builtins import str
from datetime import datetime, timedelta

import pytz
from celery import shared_task
from celery.task.control import inspect
from celery.utils.log import get_task_logger
from django.conf import settings as ontask_settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.translation import ugettext

from action.models import Action
from action.payloads import JSONPayload, CanvasEmailPayload, EmailPayload
from action.send import send_canvas_emails, send_json, send_emails
from dataops.sql import table_queries
from dataops.models import PluginRegistry
from dataops.plugin.plugin_manager import run_plugin
import dataops.sql.row_queries
from logs.models import Log
from scheduler.models import ScheduledAction
from workflow.models import Workflow
from workflow.ops import do_workflow_update_lusers

logger = get_task_logger('celery_execution')


def celery_is_up():
    """Check if celery is up.

    :return: Boolean encoding if the process is running
    """
    # Verify that celery is running!
    try:
        inspect().stats()
    except Exception:
        return False

    return True


def get_log_item(log_id):
    """
    Given a log_id, fetch it from the Logs table. This is the object used to
    write all the diagnostics.

    :param log_id: PK of the Log object to get
    :return:
    """

    log_item = Log.objects.filter(pk=log_id).first()
    if not log_item:
        # Not much can be done here. Call has no place to report error...
        logger.error(
            ugettext('Incorrect execution request with log_id {0}').format(
                log_id
            )
        )

    return log_item


def get_task_user(user_id):
    """
    Fetch a user given its id
    :param user_id: User to fetch
    :return: Raise exception if not found, or return the object
    """
    # Get the user
    user = get_user_model().objects.get(id=user_id)
    if not user:
        raise Exception(
            ugettext('Unable to find user with id {0}').format(user_id)
        )
    return user


def get_task_workflow(user, workflow_id):
    """
    Obtain the workflow with the given id and from the given user
    :param user: User object
    :param workflow_id: Workflow id
    :return: Workflow object or exception
    """

    # Get the workflow
    workflow = Workflow.objects.filter(user=user, pk=workflow_id).first()
    if not workflow:
        raise Exception(
            ugettext('Unable to find workflow with id {0}').format(
                workflow_id
            )
        )

    return workflow


def get_task_action(user, action_id):
    """
    Obtain the action with the given id and from the given user
    :param user: User object
    :param action_id: Action id
    :return: Action object or exception
    """

    # Get the action
    action = Action.objects.filter(user=user, pk=action_id).first()
    if not action:
        raise Exception(
            ugettext('Unable to find action with id {0}').format(
                action_id
            )
        )

    return action


def get_execution_items(user_id, action_id, log_id):
    """
    Given a set of ids, get the objects from the DB
    :param user_id: User id
    :param action_id: Action id (to be executed)
    :param log_id: Log id (to store execution report)
    :return: (user, action, log)
    """

    # Get the objects
    user = get_user_model().objects.get(id=user_id)
    action = Action.objects.get(id=action_id)

    # Set the log in the action
    log_item = Log.objects.get(pk=log_id)
    if action.last_executed_log != log_item:
        action.last_executed_log = log_item
        action.save()

    # Update some fields in the log
    log_item.payload['datetime'] = \
        str(datetime.now(pytz.timezone(ontask_settings.TIME_ZONE)))
    log_item.payload['filter_present'] = action.get_filter() is not None
    log_item.save()

    return user, action, log_item


@shared_task
def send_email_messages(
    user_id: int,
    log_id: int,
    action_info: EmailPayload
) -> bool:
    """Task to invoke send_messages to send email messages from action.

    This function invokes send_messages in action, gets the message
    that may be sent as a result, and records the appropriate events.

    :param user_id: Id of User object that is executing the action
    :param log_id: Id of the log object where the status has to be reflected
    :param action_info: EmailPayload object with the required pairs key, value

    :return: bool stating if execution has been correct
    """
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    try:
        user = get_task_user(user_id)
        action = get_task_action(user, action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        send_emails(
            user,
            action,
            log_item,
            action_info)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        return False

    return True


@shared_task
def send_canvas_email_messages(
    user_id: int,
    log_id: int,
    action_info: CanvasEmailPayload
) -> bool:
    """
    This function invokes send_messages in action, gets the message
    that may be sent as a result, and records the appropriate events.

    :param user_id: Id of User object that is executing the action
    :param action_id: Id of Action object from where the messages are taken
    :param subject: String for the email subject
    :param email_column: Name of the column to extract email addresses
    :param exclude_values: List of values to exclude from the mailing
    :param target_url: The name of the server to use to send email
    :param log_id: Id of the log object where the status has to be reflected
    :return: bool stating if execution has been correct
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    try:
        user = get_task_user(user_id)
        action = get_task_action(user, action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        send_canvas_emails(
            user,
            action,
            log_item,
            action_info,
        )

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()

        return False

    return True


@shared_task
def send_json_objects(
    user_id: int,
    log_id: Log,
    action_info: JSONPayload,
) -> bool:
    """Invokes send_json in action

    Gets the JSON objects that may be sent as a result, and records the
    appropriate events.

    :param user_id: Id of User object that is executing the action
    :param action_id: Id of Action object from where the messages are taken
    :param token: String to include as authorisation token
    :param key_column: Key column name to use to exclude elements (if needed)
    :param exclude_values: List of values to exclude from the mailing
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing
    """
    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user = get_task_user(user_id)
        action = get_task_action(user, action_info['action_id'])

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        send_json(user, action, log_item, action_info)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        to_return = False

    return to_return


@shared_task
def increase_track_count(method, get_dict):
    """
    Function to process track requests asynchronously.

    :param method: GET or POST received in the request
    :param get_dict: GET dictionary received in the request
    :return: If correct, increases one row of the DB by one
    """

    if method != 'GET':
        # Only GET requests are accepted
        logger.error(ugettext('Non-GET request received in Track URL'))
        return False

    # Obtain the track_id from the request
    track_id = get_dict.get('v', None)
    if not track_id:
        logger.error(ugettext('No track_id found in request'))
        # No track id, nothing to do
        return False

    # If the track_id is not correctly signed, finish.
    try:
        track_id = signing.loads(track_id)
    except signing.BadSignature:
        logger.error(ugettext('Bad signature in track_id'))
        return False

    # The request is legit and the value has been verified. Track_id has now
    # the dictionary with the tracking information

    # Get the objects related to the ping
    user = get_user_model().objects.filter(email=track_id['sender']).first()
    if not user:
        logger.error(
            ugettext('Incorrect user email {0}').format(track_id['sender'])
        )
        return False

    action = Action.objects.filter(pk=track_id['action']).first()
    if not action:
        logger.error(
            ugettext('Incorrect action id {0}').format(track_id['action'])
        )
        return False

    # Extract the relevant fields from the track_id
    column_dst = track_id.get('column_dst', '')
    column_to = track_id.get('column_to', '')
    msg_to = track_id.get('to', '')

    column = action.workflow.columns.filter(name=column_dst).first()
    if not column:
        # If the column does not exist, we are done
        logger.error(
            ugettext('Column {0} does not exist').format(column_dst)
        )
        return False

    log_payload = {'to': msg_to,
                   'email_column': column_to,
                   'column_dst': column_dst
                   }

    # If the track comes with column_dst, the event needs to be reflected
    # back in the data frame
    if column_dst:
        try:
            # Increase the relevant cell by one
            dataops.sql.row_queries.increase_row_integer(
                action.workflow.get_data_frame_table_name(),
                column_dst,
                column_to,
                msg_to
            )
        except Exception as e:
            log_payload['EXCEPTION_MSG'] = str(e)
        else:
            # Get the tracking column and update all the conditions in the
            # actions that have this column as part of their formulas
            # FIX: Too aggressive?
            track_col = action.workflow.columns.get(name=column_dst)
            for action in action.workflow.actions.all():
                action.update_n_rows_selected(track_col)

    # Record the event
    Log.objects.register(user,
                         Log.ACTION_EMAIL_READ,
                         action.workflow,
                         log_payload)

    return True


@shared_task
def run_plugin_task(user_id,
                    workflow_id,
                    plugin_id,
                    input_column_names,
                    output_column_names,
                    output_suffix,
                    merge_key,
                    parameters,
                    log_id):
    """

    Execute the run method in a plugin with the dataframe from the given
    workflow

    :param user_id: Id of User object that is executing the action
    :param workflow_id: Id of workflow being processed
    :param plugin_id: Id of the plugin being executed
    :param input_column_names: List of input column names
    :param output_column_names: List of output column names
    :param output_suffix: Suffix that is added to the output column names
    :param merge_key: Key column to use in the merge
    :param parameters: Dictionary with the parameters to execute the plug in
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing, the result is stored in the log with log_id
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user = get_task_user(user_id)

        workflow = get_task_workflow(user, workflow_id)

        plugin_info = PluginRegistry.objects.filter(pk=plugin_id).first()
        if not plugin_info:
            raise Exception(
                ugettext('Unable to load plugin with id {0}').format(
                    plugin_id
                )
            )

        # Set the status to "executing" before calling the function
        log_item.payload['status'] = 'Executing'
        log_item.save()

        # Invoke plugin execution
        run_plugin(workflow,
                   plugin_info,
                   input_column_names,
                   output_column_names,
                   output_suffix,
                   merge_key,
                   parameters)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        to_return = False

    return to_return


@shared_task
def workflow_update_lusers(user_id, workflow_id, log_id):
    """
    Recalculate the elements in field lusers of the workflow based on the fields
    luser_email_column and luser_email_column_MD5

    :param user_id: Id of User object that is executing the action
    :param workflow_id: Id of workflow being processed
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing, the result is stored in the log with log_id
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user = get_task_user(user_id)

        workflow = get_task_workflow(user, workflow_id)

        do_workflow_update_lusers(workflow, log_item)

        # Reflect status in the log event
        log_item.payload['status'] = 'Execution finished successfully'
        log_item.save()
    except Exception as e:
        log_item.payload['status'] = \
            ugettext('Error: {0}').format(e)
        log_item.save()
        to_return = False

    return to_return


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
                {'action': item.action.name,
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

            result = send_email_messages(item.user.id,
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
                {'action': item.action.name,
                 'action_id': item.action.id,
                 'exclude_values': item.exclude_values,
                 'key_column': key_column,
                 'status': 'Preparing to execute',
                 'target_url': item.action.target_url})

            # Send the objects
            result = send_json_objects(item.user.id,
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
                {'action': item.action.name,
                 'action_id': item.action.id,
                 'email_column': item.item_column.name,
                 'execute': item.execute.isoformat(),
                 'exclude_values': item.exclude_values,
                 'from_email': item.user.email,
                 'status': 'Preparing to execute',
                 'subject': subject,
                 }
            )

            result = send_canvas_email_messages(item.user_id,
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
