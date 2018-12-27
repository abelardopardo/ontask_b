# -*- coding: utf-8 -*-


from builtins import object
import datetime
import itertools
import re

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import URLValidator
from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from dataops import formula_evaluation, pandas_db
from dataops.formula_evaluation import (
    get_variables, evaluate_top_node,
    evaluate_node_text
)
from logs.models import Log
from ontask import OnTaskException
from workflow.models import Workflow, Column

# Regular expressions detecting the use of a variable, or the
# presence of a "{% MACRONAME variable %} construct in a string (template)
var_use_res = [
    re.compile('(?P<mup_pre>{{\s+)(?P<vname>.+?)(?P<mup_post>\s+\}\})'),
    re.compile('(?P<mup_pre>{%\s+if\s+)(?P<vname>.+?)(?P<mup_post>\s+%\})')
]


class Action(models.Model):
    """
    @DynamicAttrs
    """

    PERSONALIZED_TEXT = 'personalized_text'
    PERSONALIZED_CANVAS_EMAIL = 'personalized_canvas_email'
    PERSONALIZED_JSON = 'personalized_json'
    SURVEY = 'survey'
    TODO_LIST = 'todo_list'

    ACTION_TYPES = [
        (PERSONALIZED_TEXT, _('Personalized text')),
        (PERSONALIZED_CANVAS_EMAIL, _('Personalized Canvas Email')),
        (SURVEY, _('Survey')),
        (PERSONALIZED_JSON, _('Personalized JSON')),
        (TODO_LIST, _('TODO List'))
    ]

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='actions')

    name = models.CharField(max_length=256,
                            blank=False,
                            null=False,
                            verbose_name=_('name'))

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True,
                                        verbose_name=_('description'))

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
        max_length=64,
        choices=ACTION_TYPES,
        default=PERSONALIZED_TEXT
    )

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(
        default=False,
        verbose_name=_('URL available to users?'),
        null=False,
        blank=False)

    # Validity window for URL availability
    active_from = models.DateTimeField(_('Action available from'),
                                       blank=True,
                                       null=True,
                                       default=None)

    active_to = models.DateTimeField(_('Action available until'),
                                     blank=True,
                                     null=True,
                                     default=None)

    # Set of columns used in the action (either to capture data in action IN
    # or present in any of the conditions in action OUT)
    columns = models.ManyToManyField(Column, related_name='actions_in')

    #
    # Field for actions PERSONALIZED_TEXT, PERSONALIZED_CAVNAS_EMAIL and
    # PERSONALIZED_JSON
    #
    # Text to be personalised for action OUT
    content = models.TextField(default='', null=False, blank=True)

    # Text to be personalised for action OUT
    target_url = models.TextField(default='', null=True, blank=True)

    #
    # Fields for action SURVEY and TODO_LIST
    #
    # Shuffle column order when creating the page to serve
    shuffle = models.BooleanField(default=False,
                                  verbose_name=_('Shuffle questions?'),
                                  null=False,
                                  blank=False)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """
        Function to ask if an action is active: the current time is within the
        interval defined by active_from - active_to.
        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not ((self.active_from and now < self.active_from) or
                    (self.active_to and self.active_to < now))

    @property
    def is_executable(self):
        """
        Function to ask if an action is correct. All actions out are correct,
        and action ins are correct if they have at least one key column and one
        non-key column.
        :return: Boolean stating correctness
        """

        if self.action_type == Action.PERSONALIZED_TEXT:
            return True

        if self.action_type == Action.PERSONALIZED_JSON or \
                self.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
            # If None or empty, return false
            if not self.target_url:
                return False

            # Validate the URL
            validator = URLValidator()
            valid_url = True
            try:
                validator(self.target_url)
            except Exception:
                valid_url = False
            return valid_url

        if self.action_type == Action.SURVEY or self.action_type == \
                Action.TODO_LIST:
            return self.columns.filter(is_key=True).exists() and \
                   self.columns.filter(is_key=False).exists()

        raise Exception('Function is_executable not implemented for action '
                        '{0}'.format(self.get_action_type_display()))

    @property
    def is_in(self):
        return self.action_type == Action.SURVEY or \
               self.action_type == Action.TODO_LIST

    @property
    def is_out(self):
        return not self.is_in

    def get_filter(self):
        return self.conditions.filter(is_filter=True).first()

    def get_content(self):
        """
        Get the action out content
        :return: context string
        """
        return self.content

    def set_content(self, content):
        """
        Set the action content and update the list of columns
        :return: Update the DB
        """
        # Assign the content and clean the new lines
        self.content = content
        self.clean_new_lines()

        # Update the list of columns used in the action
        cond_names = self.get_action_conditions()
        colnames = list(itertools.chain.from_iterable(
            [get_variables(x.formula)
             for x in self.conditions.filter(name__in=cond_names)]
        ))
        self.columns.add(*[x for x in self.workflow.columns.filter(
            name__in=colnames
        )])

    def get_action_conditions(self):
        """
        Return the list of contition names used in the macros contained in
        the action content field
        :return: list of condition names
        """

        result = []
        # Loop over the regular expressions, match the expressions and extract
        # the list of vname fields.
        for rexpr in var_use_res:
            result += [x.group('vname') for x in rexpr.finditer(self.content)]
        return result

    def clean_new_lines(self):
        """
        Function that removes the new lines from the middle of the macros in
        the action content

        :return: new text with the newlines in the middle of the macros removed
        """
        self.content = re.sub(
            '{%(?P<varname>[^%}]+)%}',
            lambda m: '{%' + m.group('varname').replace('\n', ' ') + '%}',
            self.content)
        self.content = re.sub(
            '{{(?P<varname>[^%}]+)}}',
            lambda m: '{{' + m.group('varname').replace('\n', ' ') + '}}',
            self.content)

    def rename_variable(self, old_name, new_name):
        """
        Function that renames a variable present in the action content
        :param old_name: Old name of the variable
        :param new_name: New name of the variable
        :return: Updates the current object
        """

        if self.action_type == self.PERSONALIZED_TEXT or \
                self.action_type == self.PERSONALIZED_JSON or \
                self.action_type == self.PERSONALIZED_CANVAS_EMAIL:
            # Need to change name appearances in content
            new_text = var_use_res[0].sub(
                lambda m: '{{ ' +
                          (new_name if m.group('vname') == escape(old_name)
                           else m.group('vname')) + ' }}',
                self.content
            )
            self.content = new_text
        else:
            # Action in: Need to change name appearances in filter
            fcond = self.get_filter()
            if fcond:
                fcond.formula = formula_evaluation.rename_variable(
                    fcond.formula, old_name, new_name
                )
                fcond.save()

        self.save()

    def update_n_rows_selected(self, column=None):
        """
        Given an action reset the field n_rows_selected in all conditions

        If the column argument is present, select only those conditions that
        have column as part of their variables.

        :param column: Optional column name to process only those
        conditions that use this column
        :return: All appropriate conditions are updated
        """

        # Get the filter, if it exists.
        filter_obj = self.get_filter()
        if filter_obj:
            # If there is a filter, update the filter and this call
            # propagates to the other conditions. Nothing else is needed.
            filter_obj.update_n_rows_selected(column=column)
            return

        # This action does not have a filter, so simply recalculate the value
        # for each of the conditions
        for cond in self.conditions.all():
            cond.update_n_rows_selected(column=column)

    def used_columns(self):
        """
        Function that returns a list of the columns being used in this
        action. These are those that are used in any condition + those used
        in the columns field (if it is an action in)

        :return: List of column objects
        """

        result = set([])

        # Accumulate all columns for all conditions
        for c in self.conditions.all():
            result = result.union(set(c.columns.all()))

        # Accumulate now those in the field columns
        for c in self.columns.all():
            result.add(c)

        return list(result)

    def get_evaluation_context(self, row_values):
        """
        Given an action and a set of row_values, prepare the dictionary with the
        condition names, attribute names and column names and their
        corresponding values.
        :param row_values: Values to use in the evaluation of conditions.
        :return: Context dictionary, or None if there has been some anomaly
        """

        # If no row values are given, there is nothing to do here.
        if row_values is None:
            # No rows satisfy the given condition
            return None

        # Step 1: Evaluate all the conditions
        condition_eval = {}
        for condition in self.conditions.filter(is_filter=False).values(
                'name', 'is_filter', 'formula'):
            # Evaluate the condition
            try:
                condition_eval[condition['name']] = evaluate_top_node(
                    condition['formula'],
                    row_values
                )
            except OnTaskException:
                # Something went wrong evaluating a condition. Stop.
                return None

        # Step 2: Create the context with the attributes, the evaluation of the
        # conditions and the values of the columns.
        attributes = self.workflow.attributes

        return dict(dict(row_values, **condition_eval), **attributes)

    class Meta(object):
        """
        Define the criteria of uniqueness with name in workflow and order by
        name
        """
        unique_together = ('name', 'workflow')
        ordering = ('name',)


class Condition(models.Model):
    """
    @DynamicAttrs
    """

    action = models.ForeignKey(Action,
                               db_index=True,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='conditions')

    name = models.CharField(max_length=256, blank=True, verbose_name=_('name'))

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True,
                                        verbose_name=_('description'))

    formula = JSONField(default=dict,
                        blank=True,
                        null=True,
                        verbose_name=_('formula'))

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name=_("Columns present in this condition"),
        related_name='conditions'
    )

    # Number or rows selected by the expression
    n_rows_selected = models.IntegerField(
        verbose_name=_('Number of rows selected'),
        default=-1,
        name='n_rows_selected',
        blank=False,
        null=False
    )

    # Field to denote if this condition is the filter of an action
    is_filter = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    def update_n_rows_selected(self, column=None, filter_formula=None):
        """
        Given a condition update the number of rows
        for which this condition will have true result. In other words,
        we calculate the number of rows for which the condition is true.

        The function implements two algorithms depending on the condition
        being a filter or not:

        Case 1: Condition is a filter

        - Evaluate the filter and update field.

        - Param filter_formula is ignored

        Case 2: Condition is NOT a filter

        - If there is a filter_formula, create the conjunction together with
        the condition formula.

        :param column: Column that has changed value (None when unknown)
        :param filter_formula: Formula provided by another filter condition
        and to take the conjunction with the condition formula.
        :return: Nothing. Effect recorded in DB objects
        """

        if column and column not in self.columns.all():
            # The column is not part of this condition. Nothing to do
            return

        # Case 1: Condition is a filter
        if self.is_filter:
            self.n_rows_selected = \
                pandas_db.num_rows(self.action.workflow.id, self.formula)
            self.save()

            # Propagate the filter effect to the rest of actions.
            for condition in self.action.conditions.filter(is_filter=False):
                # Update the rest of conditions. The column=None because
                # the filter has changed, thus the condition needs to be
                # reevaluated regardless.
                condition.update_n_rows_selected(
                    column=None,
                    filter_formula=self.formula
                )
            return

        # Case 2: Condition is NOT a filter
        # Get the filter formula from the action if it exists
        if not filter_formula:
            filter_obj = self.action.conditions.filter(is_filter=True).first()
            if filter_obj:
                filter_formula = filter_obj.formula

        formula = self.formula
        if filter_formula:
            # There is a formula to add to the condition, create a conjunction
            formula = {'condition': 'AND',
                       'not': False,
                       'rules': [filter_formula, self.formula],
                       'valid': True
                       }
        self.n_rows_selected = pandas_db.num_rows(
            self.action.workflow.id, formula)
        self.save()

        return

    def get_formula_text(self):
        """
        Return the content of the formula in a string that is human readable
        :return: String
        """

        return evaluate_node_text(self.formula)[1:-1]

    def __str__(self):
        return self.name

    class Meta(object):
        """
        The unique criteria here is within the action, the name and being a
        filter. We may choose to name a filter and a condition with the same
        name (no need to restrict it)
        """
        unique_together = ('action', 'name', 'is_filter')
        ordering = ('created',)
