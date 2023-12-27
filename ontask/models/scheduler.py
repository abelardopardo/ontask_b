"""Model is to store process to execute in the platform at a certain time."""
import json

from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask

from ontask import simplify_datetime_str
from ontask.models.action import Action
from ontask.models.common import (
    CHAR_FIELD_MID_SIZE, CreateModifyFields, NameAndDescription, Owner,
)
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

OPERATION_TYPES = {
    Log.ACTION_RUN_PERSONALIZED_EMAIL:
        Log.LOG_TYPES[Log.ACTION_RUN_PERSONALIZED_EMAIL],
    Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL:
        Log.LOG_TYPES[Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL],
    Log.ACTION_RUN_PERSONALIZED_JSON:
        Log.LOG_TYPES[Log.ACTION_RUN_PERSONALIZED_JSON],
    Log.ACTION_RUN_JSON_REPORT: Log.LOG_TYPES[Log.ACTION_RUN_JSON_REPORT],
    Log.ACTION_RUN_EMAIL_REPORT: Log.LOG_TYPES[Log.ACTION_RUN_EMAIL_REPORT],
    Log.WORKFLOW_INCREASE_TRACK_COUNT: Log.LOG_TYPES[
        Log.WORKFLOW_INCREASE_TRACK_COUNT],
    Log.PLUGIN_EXECUTE: Log.LOG_TYPES[Log.PLUGIN_EXECUTE],
    Log.WORKFLOW_UPDATE_LUSERS: Log.LOG_TYPES[Log.WORKFLOW_UPDATE_LUSERS],
    Log.WORKFLOW_DATA_CANVAS_COURSE_UPLOAD:
        Log.LOG_TYPES[Log.WORKFLOW_DATA_CANVAS_COURSE_UPLOAD],
}


class ScheduledOperation(Owner, NameAndDescription, CreateModifyFields):
    """Objects representing the scheduled operations.

    @DynamicAttrs
    """

    # Type of event logged see above
    operation_type = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=False,
        blank=False,
        choices=[(key, value) for key, value in OPERATION_TYPES.items()])

    # Time of execution
    execute_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Start of execution period'))

    # Crontab string encoding the frequency of execution (if  needed
    frequency = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=False,
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
        related_name='scheduled_operation')

    # JSON element with additional information
    payload = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('payload'))

    def delete_task(self):
        """Delete the task if present."""
        if self.task:
            self.task.delete()

    def log(self, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'Scheduled id': self.id,
            'Scheduled name': self.name,
            'Scheduled execute': simplify_datetime_str(self.execute_start),
            'Scheduled frequency': self.frequency,
            'Scheduled execute until': simplify_datetime_str(
                self.execute_until),
            'Scheduled status': self.status,
            'Scheduled workflow': self.workflow.name,
            'Scheduled payload': json.dumps(self.payload)}

        if self.action:
            payload['action'] = self.action.name
            payload['action_id'] = self.action.id

        payload.update(kwargs)
        return Log.objects.register(
            self.user,
            operation_type,
            self.workflow,
            payload)

    def __str__(self):
        """Return the name translation."""
        return self.name

    class Meta:
        """Define the uniqueness criteria with name and workflow."""

        unique_together = ('name', 'workflow')
