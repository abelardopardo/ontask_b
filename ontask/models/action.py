# -*- coding: utf-8 -*-

"""Models for Actions, Conditions, and pairs (column, condition)."""

import datetime
import re
from builtins import object
from typing import List

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import URLValidator
from django.db import models
from django.utils import functional, html
from django.utils.translation import ugettext_lazy as _

import ontask
from ontask.dataops.formula import EVAL_TXT, evaluate_formula, evaluation
from ontask.dataops.sql import get_num_rows, select_ids_all_false
from ontask.models.logs import Log
from ontask.models.workflow import Workflow
from ontask.models import Column, CHAR_FIELD_MID_SIZE, CHAR_FIELD_LONG_SIZE

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


class Condition(models.Model):
    """Define object to store mainly a formula.

    The object also encodes:
    - is filter or not
    - list of columns in the support of the formula
    - number of rows for which the formula is true

    @DynamicAttrs
    """

    action = models.ForeignKey(
        Action,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='conditions',
    )

    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=True,
        verbose_name=_('name'),
    )

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'),
    )

    formula = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('formula'),
    )

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name=_('Columns present in this condition'),
        related_name='conditions',
    )

    # Number or rows selected by the expression
    n_rows_selected = models.IntegerField(
        verbose_name=_('Number of rows selected'),
        default=-1,
        name='n_rows_selected',
        blank=False,
        null=False,
    )

    # Field to denote if this condition is the filter of an action
    is_filter = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    def update_n_rows_selected(self, column=None, filter_formula=None):
        """Calculate the number of rows for which condition is true.

        Given a condition update the number of rows
        for which this condition will have true result.

        :param column: Column that has changed value (None when unknown)
        :param filter_formula: Formula provided by another filter condition
        and to take the conjunction with the condition formula.
        :return: Nothing. Effect recorded in DB objects
        """
        if column and column not in self.columns.all():
            # The column is not part of this condition. Nothing to do
            return

        formula = self.formula
        if filter_formula:
            # There is a formula to add to the condition, create a conjunction
            formula = {
                'condition': 'AND',
                'not': False,
                'rules': [filter_formula, self.formula],
                'valid': True,
            }

        new_count = get_num_rows(
            self.action.workflow.get_data_frame_table_name(),
            formula,
        )
        if new_count != self.n_rows_selected:
            # Reset the field in the action storing rows with all conditions
            # false. Needs to be recalculated because there is at least one
            # condition that has changed its count. Flush the field to None
            self.action.rows_all_false = None
            self.action.save()

        self.n_rows_selected = new_count
        self.save()

    def get_formula_text(self):
        """Translate the formula to plain text.

        Return the content of the formula in a string that is human readable
        :return: String
        """
        return evaluate_formula(self.formula, EVAL_TXT)

    def __str__(self):
        """Render string."""
        return self.name

    class Meta(object):
        """Define unique criteria and ordering.

        The unique criteria here is within the action, the name and being a
        filter. We may choose to name a filter and a condition with the same
        name (no need to restrict it)
        """

        unique_together = ('action', 'name', 'is_filter')
        ordering = ['-is_filter', 'name']


class ActionColumnConditionTuple(models.Model):
    """Represent tuples (action, column, condition).

    These objects are to:

    1) Represent the collection of columns attached to a regular action

    2) If the action is a survey, see if the question has a condition attached
    to it to decide its presence in the survey.

    @DynamicAttrs
    """

    action = models.ForeignKey(
        Action,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='column_condition_pair',
    )

    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='column_condition_pair',
    )

    condition = models.ForeignKey(
        Condition,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name='column_condition_pair',
    )

    class Meta(object):
        """Define uniqueness with name in workflow and order by name."""

        unique_together = ('action', 'column', 'condition')
        ordering = ['column__position']
