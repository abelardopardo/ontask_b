# -*- coding: utf-8 -*-

"""Model is to store process to execute in the platform at a certain time."""

import json
from typing import Optional

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask import simplify_datetime_str
from ontask.models import Column
from ontask.models.action import Action
from ontask.models.basic import CreateModifyFields, NameAndDescription
from ontask.models.const import CHAR_FIELD_MID_SIZE
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

RUN_ACTION_PERSONALIZED_TEXT = 'run_action_personalized_text'
RUN_ACTION_PERSONALIZED_JSON = 'run_action_personalized_json'
RUN_ACTION_SEND_LIST = 'run_action_send_list'
RUN_ACTION_SEND_LIST_JSON = 'run_action_send_list_json'
RUN_ACTION_RUBRIC_TEXT = 'run_action_rubric_text'

OPERATION_TYPES = [
    (RUN_ACTION_PERSONALIZED_TEXT, _('Run personali=zed text action')),
    (RUN_ACTION_PERSONALIZED_JSON, _('Run personalized JSON action')),
    (RUN_ACTION_SEND_LIST, _('Run send list action')),
    (RUN_ACTION_SEND_LIST_JSON, _('Run send JSON list action')),
    (RUN_ACTION_RUBRIC_TEXT, _('Run rubrict text action')),
]


class ScheduledOperation(NameAndDescription, CreateModifyFields):
    """Objects encoding the scheduling of a send email action.

    @DynamicAttrs
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False)

    # Type of event logged see above
    operation_type = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=False,
        blank=False,
        choices=OPERATION_TYPES)

    # Time of execution
    execute = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name=_('When to execute this action'))

    # Time to finish the execution
    execute_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(
            'End of execution period (if executing multiple times)'))

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

    def log(self, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'action': self.action.name,
            'action_id': self.action.id,
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

    class Meta(object):
        """Define the criteria of uniqueness with name and action."""

        unique_together = ('name', 'action')
