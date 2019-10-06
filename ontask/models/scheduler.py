# -*- coding: utf-8 -*-

"""Model is to store process to execute in the platform at a certain time."""

import json

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask import simplify_datetime_str
from ontask.models import Column
from ontask.models.action import Action
from ontask.models.const import CHAR_FIELD_LONG_SIZE
from ontask.models.logs import Log


class ScheduledAction(models.Model):
    """Objects encoding the scheduling of a send email action.

    @DynamicAttrs
    """

    STATUS_CREATING = 'creating'
    STATUS_PENDING = 'pending'
    STATUS_EXECUTING = 'executing'
    STATUS_DONE = 'done'
    STATUS_DONE_ERROR = 'done_error'

    SCHEDULED_STATUS = [
        (STATUS_CREATING, _('Creating')),
        (STATUS_PENDING, _('Pending')),
        (STATUS_EXECUTING, _('Executing')),
        (STATUS_DONE, _('Finished')),
        (STATUS_DONE_ERROR, _('Finished with error')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False)

    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name=_('name'))

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'))

    # The action used in the scheduling
    action = models.ForeignKey(
        Action,
        db_index=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='scheduled_actions')

    # Time of creation
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Time of execution
    execute = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name=_('When to execute this action'))

    # Time to finish the execution
    execute_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('End of execution period (if executing multiple times)'))

    # Status of the entry (pending, running or done)
    status = models.CharField(
        name='status',
        max_length=256,
        blank=False,
        choices=SCHEDULED_STATUS,
        verbose_name=_('Execution Status'))

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

    # Reference to the record of the last execution
    last_executed_log = models.ForeignKey(
        Log,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    # JSON element with additional information
    payload = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('payload'))

    def item_column_name(self):
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
            'item_column': self.item_column.name,
            'status': self.status,
            'exclude_values': self.exclude_values,
            'payload': json.dumps(self.payload)}

        payload.update(kwargs)
        return Log.objects.register(
            self.user,
            operation_type,
            self.action.workflow,
            payload)

    class Meta:
        """Define the criteria of uniqueness with name and action."""

        unique_together = ('name', 'action')
