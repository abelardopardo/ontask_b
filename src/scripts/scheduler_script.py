# -*- coding: utf-8 -*-
"""Script to execute operations that have been previously scheduled using the
web interface. This file is supposed to be executed at certain time intervals
using an application such as crontab or similar. It checks the database for
the presence of operations that have to be executed, and runs them. This
script is not intended to manage the execution of repeating tasks,
but instead, those actions that are programmed to execute at a certain point
in time."""
from __future__ import unicode_literals, print_function

import datetime
import getopt
import logging
import shlex
import sys

import pytz
from django.conf import settings as ontask_settings
from django.utils.translation import ugettext_lazy as _

import logs
from core import settings as core_settings
from ontask.tasks import send_email_messages
from scheduler.models import ScheduledEmailAction

# Get the logger object
logger = logging.getLogger(__name__)


def execute_email_actions(debug):
    """
    Function that selects the entries in the DB that are due, and proceed with
    the execution.

    :return:
    """
    # Get the current date/time
    now = datetime.datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))

    # Get the minute interval considered in OnTask
    minute_step = str(getattr(core_settings, 'MINUTE_STEP'))

    # Calculate a window with half the interval in the past and half in the
    # future to reduce latency of execution.
    after = now - datetime.timedelta(minutes=(float(minute_step) + 5) / 2)
    before = now + datetime.timedelta(minutes=(float(minute_step) + 5) / 2)
    # Get all the actions that are with state pending and before the current
    # date/time
    s_items = ScheduledEmailAction.objects.filter(
        type='email_send',
        status=0,  # Pending
        execute__lt=before,
        execute__gt=after
    )
    logger.info(str(s_items.count()) + ' actions pending execution')

    # If the number of tasks to execute is zero, we are done.
    if s_items.count() == 0:
        return

    # Check if some of the tasks are older than the minute step and flag it
    # as a warning.
    n_old_items = s_items.filter(execute__lt=after).count()
    if n_old_items != 0:
        logger.warning(
            """{0} tasks pending to execute with a delay longer than
               the defined minute step ({1} minutes).""".format(
                str(n_old_items),
                minute_step
            )
        )

    for item in s_items:
        if debug:
            logger.info('Starting execution of task ' + str(item.id))

        # Set item to running
        item.status = 1  # Running

        # Execute an email task that contains:
        # - action id
        # - subject
        # - email column
        # - send_confirmation
        # - track_read

        # Get additional parameters for the log
        cc_email = [x.strip() for x in cc_email.split(',') if x]
        bcc_email = [x.strip() for x in bcc_email.split(',') if x]

        # Log the event
        log_item = logs.ops.put(item.user,
                                'schedule_email_execute',
                                item.action.workflow,
                                {'action': item.action.name,
                                 'action_id': item.action.id,
                                 'execute': item.execute.isoformat(),
                                 'subject': item.subject,
                                 'email_column': item.email_column.name,
                                 'cc_email': cc_email,
                                 'bcc_email': bcc_email,
                                 'send_confirmation': item.send_confirmation,
                                 'track_read': item.track_read,
                                 'status': 'pre-execution'})

        send_email_messages(item.user.id,
                            item.action.id,
                            item.subject,
                            item.email_column.name,
                            item.user.email,
                            cc_email,
                            bcc_email,
                            item.send_confirmation,
                            item.track_read,
                            [], # TODO, include this as a possibility
                            log_item.id)

        # Store the resulting message in the record
        item.message = \
            _('Operation executed. Status available in Log {0}').format(
                log_item.id
            )

        # Save the new status in the DB
        item.save()


def run(*script_args):
    """
    Scrip to execute previously scheduled tasks. Example of its

    python manage.py runscript scheduler --script-args "-d "

    :param script_args: Arguments given to the script.
            -d Turns on debug
    :return: Changes reflected in the db
    """

    # If there is no argument given, bomb out.
    if len(script_args) == 0:
        print(run.__doc__)
        sys.exit(1)

    # Parse the arguments
    argv = shlex.split(script_args[0])

    # Default values for the arguments
    debug = False

    # Parse options
    try:
        opts, args = getopt.getopt(argv, "d")
    except getopt.GetoptError as e:
        print(e.msg)
        print(run.__doc__)
        sys.exit(2)

    # Store option values
    for optstr, value in opts:
        if optstr == "-d":
            debug = True

    # Starting execution
    if debug:
        logger.info('Starting execution')

    # Executing email actions
    if debug:
        logger.info('Starting to execute email actions')

    execute_email_actions(debug)

    # Finishing execution
    if debug:
        logger.info('Finished execution')
