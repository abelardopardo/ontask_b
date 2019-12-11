# -*- coding: utf-8 -*-

"""Model is to store process to execute in the platform at a certain time."""
import json
from typing import Optional

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import PeriodicTask

from ontask import simplify_datetime_str
from ontask.models import Column
from ontask.models.action import Action
from ontask.models.common import (
    CHAR_FIELD_MID_SIZE, CreateModifyFields, NameAndDescription, Owner)
from ontask.models.logs import Log
from ontask.models.workflow import Workflow

STATUS_CREATING = 'creating'
STATUS_PENDING = 'pending'
STATUS_EXECUTING = 'executing'
STATUS_DONE = 'done'
STATUS_DONE_ERROR = 'done_error'

SCHEDULED_STATUS_SIZE = 256

SCHEDULED_STATUS = [
    (STATUS_CREATING, _('Creating')),
    (STATUS_PENDING, _('Pending')),
    (STATUS_EXECUTING, _('Executing')),
    (STATUS_DONE, _('Finished')),
    (STATUS_DONE_ERROR, _('Finished with error')),
]

RUN_ACTION = 'run_action_'
RUN_ACTION_PERSONALIZED_TEXT = RUN_ACTION + Action.PERSONALIZED_TEXT
RUN_ACTION_PERSONALIZED_JSON = RUN_ACTION + Action.PERSONALIZED_JSON
RUN_ACTION_EMAIL_LIST = RUN_ACTION + Action.EMAIL_LIST
RUN_ACTION_JSON_LIST = RUN_ACTION + Action.JSON_LIST
RUN_ACTION_RUBRIC_TEXT = RUN_ACTION + Action.RUBRIC_TEXT

OPERATION_TYPES = {
    RUN_ACTION_PERSONALIZED_TEXT: _('Run personalized text action'),
    RUN_ACTION_PERSONALIZED_JSON: _('Run personalized JSON action'),
    RUN_ACTION_EMAIL_LIST: _('Run send list action'),
    RUN_ACTION_JSON_LIST: _('Run send JSON list action'),
    RUN_ACTION_RUBRIC_TEXT: _('Run rubrict text action'),
}


class ScheduledOperation(Owner, NameAndDescription, CreateModifyFields):
    """Objects encoding the scheduling of a send email action.

    @DynamicAttrs
    """

    # Type of event logged see above
    operation_type = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=False,
        blank=False,
        choices=OPERATION_TYPES.items())

    # Time of execution
    execute = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('When to execute this action'))

    # Crontab string encoding the frequency of execution (if  needed
    frequency = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=True,
        blank=True,
        default='')

    # Time to finish the execution
    execute_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(
            'End of execution period (Optional)'))

    # Status of the entry (pending, running or done)
    status = models.CharField(
        name='status',
        max_length=SCHEDULED_STATUS_SIZE,
        blank=False,
        choices=SCHEDULED_STATUS,
        verbose_name=_('Execution Status'))

    # Reference to the record of the last execution
    last_executed_log = models.ForeignKey(
        Log,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    # The action used in the scheduling
    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='scheduled_operations')

    # The action used in the scheduling
    action = models.ForeignKey(
        Action,
        db_index=True,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='scheduled_operations')

    # Key to the periodic table in django_celery_beat
    task = models.OneToOneField(
        PeriodicTask,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name=_('scheduled_operation'))

    # Column object denoting the one used to differentiate elements
    item_column = models.ForeignKey(
        Column,
        db_index=False,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='scheduled_actions',
        verbose_name=_('Column to select the elements for the action'))

    # JSON element with values to exclude from item selection.
    exclude_values = JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('exclude values'))

    # JSON element with additional information
    payload = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('payload'))

    def item_column_name(self) -> Optional[str]:
        """Column name or None."""
        return self.item_column.name if self.item_column else None

    @staticmethod
    def validate_times(execute, frequency, execute_until) -> bool:
        """Verify that the execute, frequency and execute_until are correct.

        There are eight possible combinations when specifying the start,
        stop and frequency parameters in the item depending if they are None or
        a valid value (execute, frequency, execute_until:

        1) None None None -> ERROR. Something is needed
        2) None None True -> ERROR. Only execute_until. Not allowed
        3) None True None -> Never ending crontab starting immediately
        4) None True True -> Crontab with an expiry date
        5) True None None -> SINGLE execution at a given date/time
        6) True None True -> ERROR: Missing frequency
        7) True True None -> Crontab that starts at a given time in the future
        8) True True True -> Crontab starting and stopping at a given time.
        """
        if not execute and not frequency:
            # Cases 1 and 2
            return False

        # Start and end are given, but there is no frequency.
        if execute and not frequency and execute_until:
            # Case 6
            return False

        return True

    def are_times_valid(self) -> bool:
        """Verify that the execute, frequency and execute_until are correct.
        """
        return self.validate_times(
            self.execute,
            self.frequency,
            self.execute_until)

    def log(self, operation_type: str, **kwargs):
        """Log the operation with the object."""
        action_name = ''
        action_id = -1
        if self.action:
            action_name = self.action.name
            action_id = self.action.id
        payload = {
            'id': self.id,
            'name': self.name,
            'action': action_name,
            'action_id': action_id,
            'execute': simplify_datetime_str(self.execute),
            'execute_until': simplify_datetime_str(self.execute_until),
            'item_column': self.item_column.name if self.item_column else '',
            'status': self.status,
            'exclude_values': self.exclude_values,
            'payload': json.dumps(self.payload)}

        payload.update(kwargs)
        return Log.objects.register(
            self.user,
            operation_type,
            self.action.workflow,
            payload)

    def __str__(self):
        """Return the name translation."""
        return self.name

    class Meta:
        """Define the criteria of uniqueness with name and action."""

        unique_together = ('name', 'action')
