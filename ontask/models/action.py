# -*- coding: utf-8 -*-

"""Action model."""

import datetime
import re
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import functional, html
from django.utils.translation import ugettext_lazy as _
import pytz

import ontask
from ontask.dataops.formula import evaluation
from ontask.dataops.sql import select_ids_all_false
from ontask.models.actioncolumnconditiontuple import ActionColumnConditionTuple
from ontask.models.basic import CreateModifyFields, NameAndDescription
from ontask.models.logs import Log
from ontask.models.workflow import Workflow

# Regular expressions detecting the use of a variable, or the
# presence of a "{% MACRONAME variable %} construct in a string (template)
VAR_USE_RES = [
    re.compile(r'(?P<mup_pre>{{\s+)(?P<vname>.+?)(?P<mup_post>\s+\}\})'),
    re.compile(r'(?P<mup_pre>{%\s+if\s+)(?P<vname>.+?)(?P<mup_post>\s+%\})'),
]

ACTION_TYPE_LENGTH = 64

ZIP_OPERATION = 'create_zip_from_action'


class ActionBase(NameAndDescription, CreateModifyFields):
    """Base abstract class for actions.

    @DynamicAttrs
    """

    PERSONALIZED_TEXT = 'personalized_text'
    PERSONALIZED_CANVAS_EMAIL = 'personalized_canvas_email'
    PERSONALIZED_JSON = 'personalized_json'
    RUBRIC_TEXT = 'rubric_text'
    EMAIL_LIST = 'send_list'
    JSON_LIST = 'send_list_json'
    SURVEY = 'survey'
    TODO_LIST = 'todo_list'

    ACTION_TYPES = [
        (PERSONALIZED_TEXT, _('Personalized text')),
        (PERSONALIZED_CANVAS_EMAIL, _('Personalized Canvas Email')),
        (SURVEY, _('Survey')),
        (PERSONALIZED_JSON, _('Personalized JSON')),
        (RUBRIC_TEXT, _('Rubric feedback')),
        (EMAIL_LIST, _('Send List')),
        (JSON_LIST, _('Send List as JSON')),
        (TODO_LIST, _('TODO List'))
    ]

    ACTION_IS_DATA_IN = {
        PERSONALIZED_TEXT: False,
        PERSONALIZED_CANVAS_EMAIL: False,
        PERSONALIZED_JSON: False,
        RUBRIC_TEXT: False,
        EMAIL_LIST: False,
        JSON_LIST: False,
        SURVEY: True,
        TODO_LIST: True,
    }

    LOAD_SUMMERNOTE = {
        PERSONALIZED_TEXT: True,
        PERSONALIZED_CANVAS_EMAIL: False,
        PERSONALIZED_JSON: False,
        RUBRIC_TEXT: True,
        EMAIL_LIST: True,
        JSON_LIST: False,
        SURVEY: False,
        TODO_LIST: False,
    }

    AVAILABLE_ACTION_TYPES = ACTION_TYPES[:]

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='actions',
    )

    # Action type
    action_type = models.CharField(
        max_length=ACTION_TYPE_LENGTH,
        choices=ACTION_TYPES,
        default=PERSONALIZED_TEXT,
    )

    # Reference to the record of the last execution
    last_executed_log = models.ForeignKey(
        Log,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Validity window for URL availability
    active_from = models.DateTimeField(
        _('Action available from'),
        blank=True,
        null=True,
        default=None,
    )

    active_to = models.DateTimeField(
        _('Action available until'),
        blank=True,
        null=True,
        default=None,
    )

    # Index of rows with all conditions false
    rows_all_false = JSONField(
        default=None,
        blank=True,
        null=True,
    )

    @functional.cached_property
    def is_in(self) -> bool:
        """Get bool stating if action is Survey or similar."""
        return self.ACTION_IS_DATA_IN[self.action_type]

    @functional.cached_property
    def is_out(self) -> bool:
        """Get bool stating if action is outputting data."""
        return not self.is_in

    @property
    def is_active(self) -> bool:
        """Calculate if the action is ready for execution.

        Function to ask if an action is active: the current time is within the
        interval defined by active_from - active_to.
        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not (
            (self.active_from and now < self.active_from)
            or (self.active_to and self.active_to < now)
        )

    def get_filter(self):
        """Get filter condition."""
        return self.conditions.filter(is_filter=True).first()

    def get_filter_formula(self):
        """Get filter condition."""
        f_obj = self.conditions.filter(is_filter=True).first()
        return f_obj.formula if f_obj else None

    def get_rows_selected(self):
        """Get the number of rows in table selected for this action."""
        action_filter = self.get_filter()
        if not action_filter:
            return self.workflow.nrows

        return action_filter.n_rows_selected

    def get_row_all_false_count(self):
        """Extract the rows for which  all conditions are false.

        Given a table and a list of conditions return the number of rows in
        which all the conditions are false. :return: Number of rows that have
        all conditions equal to false
        """
        if self.rows_all_false is None:
            if not self.workflow.has_data_frame():
                # Workflow does not have a dataframe
                raise ontask.OnTaskException(
                    'Workflow without DF in get_table_row_count_all_false',
                )

            # Separate filter from conditions
            filter_item = self.conditions.filter(is_filter=True).first()
            cond_list = self.conditions.filter(is_filter=False)

            if not cond_list:
                # Condition list is either None or empty. No restrictions.
                return 0

            # Workflow has a data frame and condition list is non empty

            # Get the list of indeces
            self.rows_all_false = select_ids_all_false(
                self.workflow.get_data_frame_table_name(),
                filter_item.formula if filter_item else None,
                cond_list.values_list('formula', flat=True),
            )

            self.save()

        return self.rows_all_false

    def update_n_rows_selected(self, column=None):
        """Reset the field n_rows_selected in all conditions.

        If the column argument is present, select only those conditions that
        have column as part of their variables.

        :param column: Optional column name to process only those conditions
        that use this column

        :return: All conditions (except the filter) are updated
        """
        start_idx = 0
        # Get the filter, if it exists.
        filter_formula = None
        conditions = self.conditions.all()
        if conditions and conditions[0].is_filter:
            # If there is a filter, update the formula
            conditions[0].update_n_rows_selected(column=column)
            filter_formula = conditions[0].formula
            start_idx = 1

        # Recalculate for the rest of conditions
        for cond in conditions[start_idx:]:
            cond.update_n_rows_selected(
                column=column,
                filter_formula=filter_formula,
            )

    def used_columns(self):
        """List of column used in the action.

        These are those that are used in any condition + those used
        in the columns field.

        :return: List of column objects
        """
        column_set = set()

        # Accumulate all columns for all conditions
        for cond in self.conditions.all():
            column_set = column_set.union(set(cond.columns.all()))

        # Accumulate now those in the field columns
        for ccpair in self.column_condition_pair.all():
            column_set.add(ccpair.column)

        return list(column_set)

    def __str__(self):
        """Render the name."""
        return self.name

    class Meta(object):
        """Make the class abstract."""

        abstract = True


class ActionDataOut(ActionBase):  # noqa Z214
    """Action representing a personalized message to send out"""

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(
        default=False,
        verbose_name=_('URL available to users?'),
        null=False,
        blank=False,
    )

    # Text to be personalised
    text_content = models.TextField(default='', blank=True)

    # URL for PERSONALIZED_JSON actions
    target_url = models.TextField(default='', blank=True)

    @property
    def has_html_text(self) -> bool:
        """Check if the action has HTML text."""
        return (
            self.text_content
            and (
                self.action_type == self.PERSONALIZED_TEXT
                or self.action_type == self.EMAIL_LIST))

    def rename_variable(
        self,
        old_name: str,
        new_name: str,
    ) -> None:
        """Rename a variable present in the action content.

        Two steps are performed. Rename the variable in the text_content, and
        rename the varaible in all the conditions.
        :param old_name: Old name of the variable
        :param new_name: New name of the variable
        :return: Updates the current object
        """
        if self.text_content:
            # Need to change name appearances in content
            self.text_content = VAR_USE_RES[0].sub(
                lambda match: '{{ ' + (
                    new_name if match.group('vname') == html.escape(old_name)
                    else match.group('vname')
                ) + ' }}',
                self.text_content,
            )
            self.save()

        # Rename the variable in all conditions
        for cond in self.conditions.all():
            cond.formula = evaluation.rename_variable(
                cond.formula, old_name, new_name)
            cond.save()

    def get_used_conditions(self) -> List[str]:
        """Get list of conditions that are used in the text_content.

        Iterate over the match of the regular expression in the content and
        concatenate the condition names.

        :return: List of condition names
        """
        cond_names = []
        for rexpr in VAR_USE_RES:
            cond_names += [
                match.group('vname')
                for match in rexpr.finditer(self.text_content)
            ]

        if self.has_html_text:
            cond_names = [
                name.replace(
                    '&amp;', '&').replace(
                    '&lt;', '<').replace(
                    '&gt;', '>').replace(
                    '&quot;', '"').replace(
                    '&#39;', "'")
                for name in cond_names]

        return cond_names

    def set_text_content(self, text_content: str):
        """Set the action content and update the list of columns."""
        # Method only used for self.is_out
        assert self.is_out

        # Assign the content and clean the new lines
        self.text_content = re.sub(
            '{%(?P<varname>[^%}]+)%}',
            lambda match: '{%' + match.group(
                'varname',
            ).replace('\n', ' ') + '%}',
            text_content,
        )
        self.text_content = re.sub(
            '{{(?P<varname>[^%}]+)}}',
            lambda match: '{{' + match.group(
                'varname',
            ).replace('\n', ' ') + '}}',
            self.text_content,
        )

        # Update the list of columns used in the action
        # Loop over the regular expressions, match the expressions and
        # extract the list of vname fields.
        cond_names = self.get_used_conditions()

        columns = self.workflow.columns.filter(
            conditions__name__in=set().union(*cond_names),
        ).distinct()
        for col in columns:
            ActionColumnConditionTuple.objects.get_or_create(
                action=self,
                column=col,
                condition=None,
            )

    class Meta(object):
        """Make this class abstract."""

        abstract = True


class ActionDataIn(models.Model):  # noqa Z214
    """Action representing a survey or "data-in" action."""

    # Shuffle questions when creating the learner page
    shuffle = models.BooleanField(
        default=False,
        verbose_name=_('Shuffle questions?'),
        null=False,
        blank=False,
    )

    class Meta(object):
        """Make this class abstract."""

        abstract = True


class Action(ActionDataOut, ActionDataIn):
    """Object storing an action: content, conditions, filter, etc."""

    @functional.cached_property
    def is_executable(self) -> bool:
        """Answer if an action is ready to execute.

        :return: Boolean stating correctness
        """
        for_out = (
            self.action_type == Action.PERSONALIZED_TEXT
            or self.action_type == Action.RUBRIC_TEXT
            or self.action_type == Action.EMAIL_LIST
            or self.action_type == Action.JSON_LIST
            or (self.action_type == Action.PERSONALIZED_CANVAS_EMAIL
                and settings.CANVAS_INFO_DICT is not None)
        )
        if for_out:
            return True

        if self.action_type == Action.PERSONALIZED_JSON:
            # Validate the URL
            valid_url = True
            try:
                URLValidator()(self.target_url)
            except ValidationError:
                valid_url = False

            return self.target_url and valid_url

        if self.is_in:
            cc_pairs = self.column_condition_pair
            return (
                cc_pairs.filter(column__is_key=True).exists()
                and cc_pairs.filter(column__is_key=False).exists()
            )

        raise Exception(
            'Function is_executable not implemented for action {0}'.format(
                self.get_action_type_display(),
            ),
        )

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'type': self.action_type,
            'workflow_id': self.workflow.id}

        if self.text_content:
            payload['content'] = self.text_content

        if self.target_url:
            payload['target_url'] = self.target_url

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.workflow,
            payload)

    class Meta(object):
        """Define uniqueness with name and workflow. Order by name."""

        unique_together = ('name', 'workflow')
        ordering = ['name']
