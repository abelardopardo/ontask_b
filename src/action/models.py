# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime
import re

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.html import escape

from dataops import formula_evaluation, pandas_db
from workflow.models import Workflow, Column

# Regular expression to detect the use of a variable in a django template
var_use_re = re.compile('{{ (?P<varname>.+?) \}\}')


class Action(models.Model):
    """
    @DynamicAttrs
    """

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        related_name='actions')

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512, default='', blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # If the action is to provide information to learners
    is_out = models.BooleanField(
        default=True,
        verbose_name='Action is provide information',
        null=False,
        blank=False)

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(
        default=False,
        verbose_name='URL available to users?',
        null=False,
        blank=False)

    # Validity window for URL availability
    active_from = models.DateTimeField(
        'Action available from',
        blank=True,
        null=True,
        default=None,
    )

    active_to = models.DateTimeField(
        'Action available until',
        blank=True,
        null=True,
        default=None
    )

    #
    # Field for action OUT
    #
    # Text to be personalised for action OUT
    content = models.TextField(
        default='',
        null=False,
        blank=True)

    #
    # Fields for action IN
    #
    # Set of columns for the personalised action IN (subset of the matrix
    # columns
    columns = models.ManyToManyField(Column, related_name='actions_in')

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
    def is_correct(self):
        """
        Function to ask if an action is correct. All actions out are correct,
        and action ins are correct if they have at least one key column and one
        non-key column.
        :return: Boolean stating correctness
        """

        return self.columns.filter(is_key=True).exists() and \
               self.columns.filter(is_key=False).exists()

    def rename_variable(self, old_name, new_name):
        """
        Function that renames a variable present in the action content
        :param old_name: Old name of the variable
        :param new_name: New name of the variable
        :return: Updates the current object
        """

        if self.is_out:
            # Action out: Need to change name appearances in content
            new_text = var_use_re.sub(
                lambda m: '{{ ' +
                          (new_name if m.group('varname') == escape(old_name)
                           else m.group('varname')) + ' }}',
                self.content
            )
            self.content = new_text
        else:
            # Action in: Need to change name appearances in filter
            fcond = self.conditions.filter(is_filter=True).first()
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
        filter = self.conditions.filter(is_filter=True).first()
        if filter:
            # If there is a filter, update the filter and this call
            # propagates to the other conditions. Nothing else is needed.
            filter.update_n_rows_selected(column=column)
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

    class Meta:
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

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512, default='', blank=True)

    formula = JSONField(default=dict, blank=True, null=True)

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name="Columns present in this condition",
        related_name='conditions')

    # Number or rows selected by the expression
    n_rows_selected = models.IntegerField(
        verbose_name='Number of rows selected',
        default=-1,
        name='n_rows_selected',
        blank=False,
        null=False)

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

    def __str__(self):
        return self.name

    class Meta:
        """
        The unique criteria here is within the action, the name and being a
        filter. We may choose to name a filter and a condition with the same
        name (no need to restrict it)
        """
        unique_together = ('action', 'name', 'is_filter')
        ordering = ('created',)
