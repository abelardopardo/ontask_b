# -*- coding: utf-8 -*-

"""Action model."""

import datetime
import re
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import URLValidator
from django.db import models
from django.utils import functional, html
from django.utils.translation import ugettext_lazy as _
import pytz

import ontask
from ontask.dataops.formula import evaluation
from ontask.dataops.sql import select_ids_all_false
from ontask.models.actioncolumnconditiontuple import ActionColumnConditionTuple
from ontask.models.const import CHAR_FIELD_LONG_SIZE, CHAR_FIELD_MID_SIZE
from ontask.models.logs import Log
from ontask.models.workflow import Workflow

# Regular expressions detecting the use of a variable, or the
# presence of a "{% MACRONAME variable %} construct in a string (template)
var_use_res = [
    re.compile(r'(?P<mup_pre>{{\s+)(?P<vname>.+?)(?P<mup_post>\s+\}\})'),
    re.compile(r'(?P<mup_pre>{%\s+if\s+)(?P<vname>.+?)(?P<mup_post>\s+%\})'),
]

ACTION_TYPE_LENGTH = 64


class Action(models.Model):  # noqa Z214
    """Object storing an action: content, conditions, filter, etc.

    @DynamicAttrs
    """

    personalized_text = ontask.PERSONALIZED_TEXT
    personalized_canvas_email = ontask.PERSONALIZED_CANVAS_EMAIL
    personalized_json = ontask.PERSONALIZED_JSON
    send_list = ontask.SEND_LIST
    send_list_json = ontask.SEND_LIST_JSON
    survey = ontask.SURVEY
    todo_list = ontask.TODO_LIST

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='actions',
    )

    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=False,
        verbose_name=_('name'),
    )

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'),
    )

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Reference to the record of the last execution
    last_executed_log = models.ForeignKey(
        Log,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Action type
    action_type = models.CharField(
        max_length=ACTION_TYPE_LENGTH,
        choices=ontask.ACTION_TYPES,
        default=personalized_text,
    )

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(
        default=False,
        verbose_name=_('URL available to users?'),
        null=False,
        blank=False,
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

    #
    # Field for actions PERSONALIZED_TEXT, PERSONALIZED_CAVNAS_EMAIL and
    # PERSONALIZED_JSON
    #
    # Text to be personalised for action OUT
    text_content = models.TextField(default='', blank=True)

    # URL for PERSONALIZED_JSON actions
    target_url = models.TextField(default='', blank=True)

    #
    # Fields for action SURVEY and TODO_LIST
    #
    # Shuffle column order when creating the page to serve
    shuffle = models.BooleanField(
        default=False,
        verbose_name=_('Shuffle questions?'),
        null=False,
        blank=False,
    )

    def __str__(self):
        """Render the name."""
        return self.name

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

    @functional.cached_property
    def is_executable(self) -> bool:
        """Answer if an action is ready to execute.

        :return: Boolean stating correctness
        """
        for_out = (
            self.action_type == Action.personalized_text
            or self.action_type == Action.send_list
            or self.action_type == Action.send_list_json
            or (self.action_type == Action.personalized_canvas_email
                and settings.CANVAS_INFO_DICT is not None)
        )
        if for_out:
            return True

        if self.action_type == Action.personalized_json:
            # Validate the URL
            valid_url = True
            try:
                URLValidator()(self.target_url)
            except Exception:
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

    @property
    def has_html_text(self) -> bool:
        return (
            self.text_content
            and (
                self.action_type == Action.PERSONALIZED_TEXT
                or self.action_type == Action.SEND_LIST))

    @functional.cached_property
    def is_in(self):
        """Get bool stating if action is Survey or similar."""
        return (
            self.action_type == Action.survey
            or self.action_type == Action.todo_list
        )

    @functional.cached_property
    def is_out(self):
        """Get bool stating if action is OUT."""
        return not self.is_in

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

    def get_used_conditions(self) -> List[str]:
        """Get list of conditions that are used in the text_content.

        Iterate over the match of the regular expression in the content and
        concatenate the condition names.

        :return: List of condition names
        """
        cond_names = []
        for rexpr in var_use_res:
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
            self.text_content = var_use_res[0].sub(
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

    def update_n_rows_selected(self, filter_formula=None, column=None):
        """Reset the field n_rows_selected in all conditions.

        If the column argument is present, select only those conditions that
        have column as part of their variables.

        :param filter_formula: If given, the evaluation of the filter
        condition is bypassed.

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
        """Lis of column used in the action.

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

    class Meta(object):
        """Define uniqueness with name and workflow. Order by name."""

        unique_together = ('name', 'workflow')
        ordering = ['name']
