"""Model for OnTask Logs."""
import json
from typing import Dict

from django.db import models
from django.db.models import JSONField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ontask.models.common import CHAR_FIELD_MID_SIZE, Owner


class LogManager(models.Manager):
    """Manager to create elements with the right parameters."""

    def register(
        self,
        user,
        name: str,
        workflow,
        payload: Dict
    ) -> 'Log':
        """Handle user, name, workflow and payload."""
        log_item = self.create(
            user=user,
            name=name,
            workflow=workflow,
            payload=payload)
        return log_item


class Log(Owner):
    """Model to encode logs in OnTask.

    @DynamicAttrs
    """

    ACTION_CANVAS_EMAIL_SENT = 'action_canvas_email_sent'
    ACTION_CLONE = 'action_clone'
    ACTION_CREATE = 'action_create'
    ACTION_DELETE = 'action_delete'
    ACTION_DOWNLOAD = 'download_zip_action'
    ACTION_EMAIL_NOTIFY = 'action_email_notify'
    ACTION_EMAIL_READ = 'action_email_read'
    ACTION_EMAIL_SENT = 'action_email_sent'
    ACTION_IMPORT = 'action_import'
    ACTION_JSON_SENT = 'action_json_sent'
    ACTION_REPORT_EMAIL_SENT = 'action_report_email_sent'
    ACTION_QUESTION_ADD = 'question_add'
    ACTION_QUESTION_REMOVE = 'question_remove'
    ACTION_TODOITEM_ADD = 'todoitem_add'
    ACTION_QUESTION_TOGGLE_CHANGES = 'question_toggle_changes'
    ACTION_TODOITEM_TOGGLE_CHANGES = 'todoitem_toggle_changes'
    ACTION_RUBRIC_CRITERION_ADD = 'action_rubric_criterion_add'
    ACTION_RUBRIC_CRITERION_EDIT = 'action_rubric_criterion_edit'
    ACTION_RUBRIC_CRITERION_DELETE = 'action_rubric_criterion_delete'
    ACTION_RUBRIC_CELL_EDIT = 'action_rubric_cell_edit'
    ACTION_RUBRIC_LOA_EDIT = 'action_rubric_loa_edit'
    ACTION_RUN_EMAIL_REPORT = 'action_run_email_report'
    ACTION_RUN_JSON_REPORT = 'action_run_json_report'
    ACTION_RUN_PERSONALIZED_CANVAS_EMAIL = (
        'action_run_personalized_canvas_email')
    ACTION_RUN_PERSONALIZED_EMAIL = 'action_run_personalized_email'
    ACTION_RUN_PERSONALIZED_JSON = 'action_run_personalized_json'
    ACTION_RUN_SURVEY = 'action_run_survey'
    ACTION_RUN_TODOLIST = 'action_run_todolist'
    ACTION_SERVE_TOGGLED = 'action_serve_toggled'
    ACTION_SERVED_EXECUTE = 'action_served_execute'
    ACTION_SURVEY_INPUT = 'survey_input'
    ACTION_TODO_INPUT = 'todo_input'
    ACTION_UPDATE = 'action_update'
    ACTION_ZIP = 'action_zip'
    ATHENA_CONNECTION_CREATE = 'athena_connection_create'
    ATHENA_CONNECTION_EDIT = 'athena_connection_edit'
    ATHENA_CONNECTION_DELETE = 'athena_connection_delete'
    ATHENA_CONNECTION_CLONE = 'athena_connection_clone'
    ATHENA_CONNECTION_TOGGLE = 'athena_connection_toggle'
    CANVAS_COURSE_QUIZ_UPDATE_CREATE = 'canvas_course_quiz_connection_create'
    CANVAS_COURSE_QUIZ_UPDATE_EDIT = 'canvas_course_quiz_connection_edit'
    CANVAS_COURSE_QUIZ_UPDATE_DELETE = 'canvas_course_quiz_connection_delete'
    CANVAS_COURSE_QUIZ_UPDATE_CLONE = 'canvas_course_quiz_connection_clone'
    CANVAS_COURSE_QUIZ_UPDATE_TOGGLE = 'canvas_course_quiz_connection_toggle'
    COLUMN_ADD = 'column_add'
    COLUMN_ADD_FORMULA = 'column_add_formula'
    COLUMN_ADD_RANDOM = 'column_add_random'
    COLUMN_CLONE = 'column_clone'
    COLUMN_DELETE = 'column_delete'
    COLUMN_EDIT = 'column_edit'
    COLUMN_RESTRICT = 'column_restrict'
    CONDITION_CLONE = 'condition_clone'
    CONDITION_CREATE = 'condition_create'
    CONDITION_DELETE = 'condition_delete'
    CONDITION_UPDATE = 'condition_update'
    PLUGIN_CREATE = 'plugin_create'
    PLUGIN_DELETE = 'plugin_delete'
    PLUGIN_EXECUTE = 'plugin_execute'
    PLUGIN_UPDATE = 'plugin_update'
    SCHEDULE_CREATE = 'schedule_create'
    SCHEDULE_EDIT = 'schedule_edit'
    SCHEDULE_DELETE = 'schedule_delete'
    SQL_CONNECTION_CLONE = 'sql_connection_clone'
    SQL_CONNECTION_CREATE = 'sql_connection_create'
    SQL_CONNECTION_DELETE = 'sql_connection_delete'
    SQL_CONNECTION_EDIT = 'sql_connection_edit'
    SQL_CONNECTION_TOGGLE = 'sql_connection_toggle'
    VIEW_CLONE = 'view_clone'
    VIEW_CREATE = 'view_create'
    VIEW_DELETE = 'view_delete'
    VIEW_EDIT = 'view_edit'
    WORKFLOW_ATTRIBUTE_CREATE = 'workflow_attribute_create'
    WORKFLOW_ATTRIBUTE_UPDATE = 'workflow_attribute_update'
    WORKFLOW_ATTRIBUTE_DELETE = 'workflow_attribute_delete'
    WORKFLOW_CLONE = 'workflow_clone'
    WORKFLOW_CREATE = 'workflow_create'
    WORKFLOW_DATA_FAILEDMERGE = 'workflow_data_failedmerge'
    WORKFLOW_DATA_FLUSH = 'workflow_data_flush'
    WORKFLOW_DATA_ROW_UPDATE = 'tablerow_update'
    WORKFLOW_DATA_ROW_CREATE = 'tablerow_create'
    WORKFLOW_DATA_ATHENA_UPLOAD = 'workflow_athena_data_upload'
    WORKFLOW_DATA_CANVAS_UPLOAD = 'workflow_canvas_data_upload'
    WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD = \
        'workflow_canvas_course_enrollment_data_upload'
    WORKFLOW_DATA_CSV_UPLOAD = 'workflow_csv_data_upload'
    WORKFLOW_DATA_EXCEL_UPLOAD = 'workflow_excel_data_upload'
    WORKFLOW_DATA_GSHEET_UPLOAD = 'workflow_gsheet_data_upload'
    WORKFLOW_DATA_S3_UPLOAD = 'workflow_se_data_upload'
    WORKFLOW_DATA_SQL_UPLOAD = 'workflow_sql_data_upload'
    WORKFLOW_DELETE = 'workflow_delete'
    WORKFLOW_IMPORT = 'workflow_import'
    WORKFLOW_INCREASE_TRACK_COUNT = 'workflow_increase_track_count'
    WORKFLOW_SHARE_ADD = 'workflow_share_add'
    WORKFLOW_SHARE_DELETE = 'workflow_share_delete'
    WORKFLOW_STAR = 'workflow_star'
    WORKFLOW_UPDATE = 'workflow_update'
    WORKFLOW_UPDATE_LUSERS = 'workflow_update_lusers'

    LOG_TYPES = {
        ACTION_CANVAS_EMAIL_SENT: _('Canvas emails sent'),
        ACTION_CLONE: _('Action cloned'),
        ACTION_CREATE: _('Action created'),
        ACTION_DELETE: _('Action deleted'),
        ACTION_DOWNLOAD: _('Download a ZIP with one file per text'),
        ACTION_EMAIL_NOTIFY: _('Notification email sent'),
        ACTION_EMAIL_READ: _('Email read'),
        ACTION_EMAIL_SENT: _('Emails sent'),
        ACTION_IMPORT: _('Action imported'),
        ACTION_JSON_SENT: _('JSON object sent'),
        ACTION_REPORT_EMAIL_SENT: _('Email with data report sent'),
        ACTION_QUESTION_ADD: _('Question added'),
        ACTION_QUESTION_REMOVE: _('Question removed'),
        ACTION_TODOITEM_ADD: _('TODO item added'),
        ACTION_QUESTION_TOGGLE_CHANGES: _('Question toggle changes'),
        ACTION_TODOITEM_TOGGLE_CHANGES: _('TODO item toggle changes'),
        ACTION_RUBRIC_CRITERION_ADD: _('Add a rubric criterion'),
        ACTION_RUBRIC_CRITERION_EDIT: _('Edit rubric criterion'),
        ACTION_RUBRIC_CRITERION_DELETE: _('Delete rubric criterion'),
        ACTION_RUBRIC_CELL_EDIT: _('Rubric cell edit'),
        ACTION_RUBRIC_LOA_EDIT: _('Rubric level of attainment edit'),
        ACTION_RUN_EMAIL_REPORT: _('Execute scheduled send report action'),
        ACTION_RUN_JSON_REPORT: _('Execute scheduled JSON report action'),
        ACTION_RUN_PERSONALIZED_CANVAS_EMAIL:
            _('Execute scheduled canvas email action'),
        ACTION_RUN_PERSONALIZED_EMAIL: _('Execute scheduled email action'),
        ACTION_RUN_PERSONALIZED_JSON: _('Execute scheduled JSON action'),
        ACTION_RUN_SURVEY: _('Execute survey'),
        ACTION_RUN_TODOLIST: _('Execute TODO list'),
        ACTION_ZIP: _('Create a zip with personalized content'),
        ACTION_SERVE_TOGGLED: _('Action URL toggled'),
        ACTION_SERVED_EXECUTE: _('Action served'),
        ACTION_SURVEY_INPUT: _('Survey data input'),
        ACTION_TODO_INPUT: _('TODO data input'),
        ACTION_UPDATE: _('Action updated'),
        ATHENA_CONNECTION_CLONE: _('Athena connection cloned'),
        ATHENA_CONNECTION_CREATE: _('Athena connection created'),
        ATHENA_CONNECTION_DELETE: _('Athena connection deleted'),
        ATHENA_CONNECTION_EDIT: _('Athena connection updated'),
        ATHENA_CONNECTION_TOGGLE: _('Athena connection toggled'),
        CANVAS_COURSE_QUIZ_UPDATE_CLONE: _('Canvas connection cloned'),
        CANVAS_COURSE_QUIZ_UPDATE_CREATE: _('Canvas connection created'),
        CANVAS_COURSE_QUIZ_UPDATE_DELETE: _('Canvas connection deleted'),
        CANVAS_COURSE_QUIZ_UPDATE_EDIT: _('Canvas connection updated'),
        CANVAS_COURSE_QUIZ_UPDATE_TOGGLE: _('Canvas connection toggled'),
        COLUMN_ADD: _('Column added'),
        COLUMN_ADD_FORMULA: _('Column with formula created'),
        COLUMN_ADD_RANDOM: _('Column with random values created'),
        COLUMN_CLONE: _('Column cloned'),
        COLUMN_DELETE: _('Column deleted'),
        COLUMN_EDIT: _('Column edited'),
        COLUMN_RESTRICT: _('Column restricted'),
        CONDITION_CLONE: _('Condition cloned'),
        CONDITION_CREATE: _('Condition created'),
        CONDITION_DELETE: _('Condition deleted'),
        CONDITION_UPDATE: _('Condition updated'),
        PLUGIN_CREATE: _('Plugin created'),
        PLUGIN_DELETE: _('Plugin deleted'),
        PLUGIN_EXECUTE: _('Plugin executed'),
        PLUGIN_UPDATE: _('Plugin updated'),
        SCHEDULE_CREATE: _('Create scheduled operation'),
        SCHEDULE_EDIT: _('Edit scheduled operation'),
        SCHEDULE_DELETE: _('Delete scheduled operation'),
        SQL_CONNECTION_CLONE: _('SQL connection cloned'),
        SQL_CONNECTION_CREATE: _('SQL connection created'),
        SQL_CONNECTION_DELETE: _('SQL connection deleted'),
        SQL_CONNECTION_EDIT: _('SQL connection updated'),
        SQL_CONNECTION_TOGGLE: _('SQL connection toggled'),
        VIEW_CREATE: _('Table view created'),
        VIEW_EDIT: _('Table view edited'),
        VIEW_DELETE: _('Table view deleted'),
        VIEW_CLONE: _('Table view cloned'),
        WORKFLOW_ATTRIBUTE_CREATE: _('New attribute in workflow'),
        WORKFLOW_ATTRIBUTE_UPDATE: _('Attributes updated in workflow'),
        WORKFLOW_ATTRIBUTE_DELETE: _('Attribute deleted'),
        WORKFLOW_CLONE: _('Workflow cloned'),
        WORKFLOW_CREATE: _('Workflow created'),
        WORKFLOW_DATA_FAILEDMERGE: _('Failed data merge into workflow'),
        WORKFLOW_DATA_FLUSH: _('Workflow data flushed'),
        WORKFLOW_DATA_ROW_CREATE: _('Table row created'),
        WORKFLOW_DATA_ROW_UPDATE: _('Table row updated'),
        WORKFLOW_DATA_ATHENA_UPLOAD: _('Athena data uploaded to workflow'),
        WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD: _(
            'Canvas course enrollment data uploaded to workflow'),
        WORKFLOW_DATA_CANVAS_UPLOAD: _('Canvas data uploaded to workflow'),
        WORKFLOW_DATA_CSV_UPLOAD: _('Upload Data from CSV File'),
        WORKFLOW_DATA_EXCEL_UPLOAD: _('Upload Data from Excel Sheet'),
        WORKFLOW_DATA_GSHEET_UPLOAD: _('Upload Data from Google Sheet'),
        WORKFLOW_DATA_S3_UPLOAD: _('Upload Data from S3 CSV source'),
        WORKFLOW_DATA_SQL_UPLOAD: _('Upload Data from SQL source'),
        WORKFLOW_DELETE: _('Workflow deleted'),
        WORKFLOW_IMPORT: _('Import workflow'),
        WORKFLOW_INCREASE_TRACK_COUNT: _('Increase workflow track count.'),
        WORKFLOW_SHARE_ADD: _('User share added'),
        WORKFLOW_SHARE_DELETE: _('User share deleted'),
        WORKFLOW_STAR: _('Toggle workflow star'),
        WORKFLOW_UPDATE: _('Workflow updated'),
        WORKFLOW_UPDATE_LUSERS: _('Update list of workflow users'),
    }

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Type of event logged see above
    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=False,
        choices=[(key, value) for key, value in LOG_TYPES.items()])

    workflow = models.ForeignKey(
        'Workflow',
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
    objects = LogManager()  # noqa: Z110

    def get_payload(self):
        """Access the payload information.

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

    def set_error_in_payload(self, msg: str):
        """Set the given MSG in error field in payload."""
        self.payload['error'] = msg
        self.save(update_fields=['payload'])

    def __str__(self):
        """Return the name translation."""
        return str(self.LOG_TYPES[self.name])

    @cached_property
    def log_user_email(self):
        """Return the user email."""
        return self.user.email
