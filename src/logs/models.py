# -*- coding: utf-8 -*-

"""Model for OnTask Logs."""

import json

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from workflow.models import Workflow


class LogManager(models.Manager):
    """Manager to create elements with the right parameters."""

    def register(self, user, name, workflow, payload):
        """Handle user, name, workflow and payload."""
        log_item = self.create(
            user=user,
            name=name,
            workflow=workflow,
            payload=payload)
        return log_item


class Log(models.Model):
    """Model to encode logs in OnTask.

    @DynamicAttrs
    """

    WORKFLOW_CREATE = 'workflow_create'
    WORKFLOW_UPDATE = 'workflow_update'
    WORKFLOW_DELETE = 'workflow_delete'
    WORKFLOW_DATA_UPLOAD = 'workflow_data_upload'
    WORKFLOW_DATA_MERGE = 'workflow_data_merge'
    WORKFLOW_DATA_FAILEDMERGE = 'workflow_data_failedmerge'
    WORKFLOW_DATA_FLUSH = 'workflow_data_flush'
    WORKFLOW_ATTRIBUTE_CREATE = 'workflow_attribute_create'
    WORKFLOW_ATTRIBUTE_UPDATE = 'workflow_attribute_update'
    WORKFLOW_ATTRIBUTE_DELETE = 'workflow_attribute_delete'
    WORKFLOW_SHARE_ADD = 'workflow_share_add'
    WORKFLOW_SHARE_DELETE = 'workflow_share_delete'
    WORKFLOW_IMPORT = 'workflow_import'
    WORKFLOW_CLONE = 'workflow_clone'
    WORKFLOW_UPDATE_LUSERS = 'workflow_update_lusers'
    COLUMN_ADD = 'column_add'
    QUESTION_ADD = 'question_add'
    COLUMN_ADD_FORMULA = 'column_add_formula'
    COLUMN_ADD_RANDOM = 'column_add_random'
    COLUMN_RENAME = 'column_rename'
    COLUMN_DELETE = 'column_delete'
    COLUMN_CLONE = 'column_clone'
    COLUMN_RESTRICT = 'column_restrict'
    ACTION_CREATE = 'action_create'
    ACTION_UPDATE = 'action_update'
    ACTION_DELETE = 'action_delete'
    ACTION_CLONE = 'action_clone'
    ACTION_EMAIL_SENT = 'action_email_sent'
    ACTION_CANVAS_EMAIL_SENT = 'action_canvas_email_sent'
    ACTION_EMAIL_NOTIFY = 'action_email_notify'
    ACTION_EMAIL_READ = 'action_email_read'
    ACTION_SERVE_TOGGLED = 'action_serve_toggled'
    ACTION_SERVED_EXECUTE = 'action_served_execute'
    ACTION_IMPORT = 'action_import'
    ACTION_JSON_SENT = 'action_json_sent'
    CONDITION_CREATE = 'condition_create'
    CONDITION_UPDATE = 'condition_update'
    CONDITION_DELETE = 'condition_delete'
    CONDITION_CLONE = 'condition_clone'
    TABLEROW_UPDATE = 'tablerow_update'
    TABLEROW_CREATE = 'tablerow_create'
    VIEW_CREATE = 'view_create'
    VIEW_EDIT = 'view_edit'
    VIEW_DELETE = 'view_delete'
    VIEW_CLONE = 'view_clone'
    FILTER_CREATE = 'filter_create'
    FILTER_UPDATE = 'filter_update'
    FILTER_DELETE = 'filter_delete'
    PLUGIN_CREATE = 'plugin_create'
    PLUGIN_UPDATE = 'plugin_update'
    PLUGIN_DELETE = 'plugin_delete'
    PLUGIN_EXECUTE = 'plugin_execute'
    SQL_CONNECTION_CREATE = 'sql_connection_create'
    SQL_CONNECTION_EDIT = 'sql_connection_edit'
    SQL_CONNECTION_DELETE = 'sql_connection_delete'
    SQL_CONNECTION_CLONE = 'sql_connection_clone'
    SCHEDULE_EMAIL_EDIT = 'schedule_email_edit'
    SCHEDULE_EMAIL_DELETE = 'schedule_email_delete'
    SCHEDULE_EMAIL_EXECUTE = 'schedule_email_execute'
    SCHEDULE_CANVAS_EMAIL_EDIT = 'schedule_canvas_email_edit'
    SCHEDULE_CANVAS_EMAIL_EXECUTE = 'schedule_canvas_email_execute'
    SCHEDULE_CANVAS_EMAIL_DELETE = 'schedule_canvas_email_delete'
    DOWNLOAD_ZIP_ACTION = 'download_zip_action'
    SCHEDULE_JSON_EDIT = 'schedule_json_edit'
    SCHEDULE_JSON_DELETE = 'schedule_json_delete'
    SCHEDULE_JSON_EXECUTE = 'schedule_json_execute'

    LOG_TYPES = [
        (WORKFLOW_CREATE, _('Workflow created')),
        (WORKFLOW_UPDATE, _('Workflow updated')),
        (WORKFLOW_DELETE, _('Workflow deleted')),
        (WORKFLOW_DATA_UPLOAD, _('Data uploaded to workflow')),
        (WORKFLOW_DATA_MERGE, _('Data merged into workflow')),
        (WORKFLOW_DATA_FAILEDMERGE, _('Failed data merge into workflow')),
        (WORKFLOW_DATA_FLUSH, _('Workflow data flushed')),
        (WORKFLOW_ATTRIBUTE_CREATE, _('New attribute in workflow')),
        (WORKFLOW_ATTRIBUTE_UPDATE, _('Attributes updated in workflow')),
        (WORKFLOW_ATTRIBUTE_DELETE, _('Attribute deleted')),
        (WORKFLOW_SHARE_ADD, _('User share added')),
        (WORKFLOW_SHARE_DELETE, _('User share deleted')),
        (WORKFLOW_IMPORT, _('Import workflow')),
        (WORKFLOW_CLONE, _('Workflow cloned')),
        (WORKFLOW_UPDATE_LUSERS, _('Update list of workflow users')),
        (COLUMN_ADD, _('Column added')),
        (COLUMN_ADD_FORMULA, _('Column with formula created')),
        (COLUMN_ADD_RANDOM, _('Column with random values created')),
        (COLUMN_RENAME, _('Column renamed')),
        (COLUMN_DELETE, _('Column deleted')),
        (COLUMN_CLONE, _('Column cloned')),
        (COLUMN_RESTRICT, _('Column restricted')),
        (ACTION_CREATE, _('Action created')),
        (ACTION_UPDATE, _('Action updated')),
        (ACTION_DELETE, _('Action deleted')),
        (ACTION_CLONE, _('Action cloned')),
        (ACTION_EMAIL_SENT, _('Emails sent')),
        (ACTION_CANVAS_EMAIL_SENT, _('Canvas Emails sent')),
        (ACTION_EMAIL_NOTIFY, _('Notification email sent')),
        (ACTION_EMAIL_READ, _('Email read')),
        (ACTION_SERVE_TOGGLED, _('Action URL toggled')),
        (ACTION_SERVED_EXECUTE, _('Action served')),
        (ACTION_IMPORT, _('Action imported')),
        (ACTION_JSON_SENT, _('Emails sent')),
        (CONDITION_CREATE, _('Condition created')),
        (CONDITION_UPDATE, _('Condition updated')),
        (CONDITION_DELETE, _('Condition deleted')),
        (CONDITION_CLONE, _('Condition cloned')),
        (TABLEROW_UPDATE, _('Table row updated')),
        (TABLEROW_CREATE, _('Table row created')),
        (VIEW_CREATE, _('Table view created')),
        (VIEW_EDIT, _('Table view edited')),
        (VIEW_DELETE, _('Table view deleted')),
        (VIEW_CLONE, _('Table view cloned')),
        (FILTER_CREATE, _('Filter created')),
        (FILTER_UPDATE, _('Filter updated')),
        (FILTER_DELETE, _('Filter deleted')),
        (PLUGIN_CREATE, _('Plugin created')),
        (PLUGIN_UPDATE, _('Plugin updated')),
        (PLUGIN_DELETE, _('Plugin deleted')),
        (PLUGIN_EXECUTE, _('Plugin executed')),
        (SQL_CONNECTION_CREATE, _('SQL connection created')),
        (SQL_CONNECTION_EDIT, _('SQL connection updated')),
        (SQL_CONNECTION_DELETE, _('SQL connection deleted')),
        (SQL_CONNECTION_CLONE, _('SQL connection cloned')),
        (SCHEDULE_EMAIL_EDIT, _('Edit scheduled email action')),
        (SCHEDULE_EMAIL_DELETE, _('Delete scheduled email action')),
        (SCHEDULE_EMAIL_EXECUTE, _('Execute scheduled email action')),
        (SCHEDULE_CANVAS_EMAIL_EDIT,
         _('Edit scheduled canvas email action')),
        (SCHEDULE_CANVAS_EMAIL_EXECUTE,
         _('Execute scheduled canvas email action')),
        (SCHEDULE_CANVAS_EMAIL_DELETE,
         _('Delete scheduled canvas email action')),
        (DOWNLOAD_ZIP_ACTION, _('Download a ZIP with personalized text')),
        (SCHEDULE_JSON_EDIT, _('Edit scheduled JSON action')),
        (SCHEDULE_JSON_DELETE, _('Delete scheduled JSON action')),
        (SCHEDULE_JSON_EXECUTE, _('Execute scheduled JSON action')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Type of event logged see above
    name = models.CharField(
        max_length=256,
        blank=False,
        choices=LOG_TYPES)

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        on_delete=models.CASCADE,
        null=True,
        related_name='logs')

    # JSON element with additional information
    payload = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('payload'))

    # Use our own manager
    objects = LogManager()

    def get_payload(self):
        """Function to access the payload information.

        If using a DB that supports JSON this function should be rewritten (
        to be transparent).

        :return: The JSON structure with the payload
        """

        if self.payload == '':
            return {}

        return json.loads(self.payload)

    def set_payload(self, payload):
        """Save the payload structure as text.

        If using a DB that supports JSON, this function should be rewritten.

        :return: Nothing.
        """
        self.payload = json.dumps(payload)

    def __unicode__(self):
        """Represent as a tuple."""
        return '%s %s %s %s' % (self.user,
                                self.created,
                                self.name,
                                self.payload)

    @cached_property
    def log_useremail(self):
        """Return the user email."""
        return self.user.email
