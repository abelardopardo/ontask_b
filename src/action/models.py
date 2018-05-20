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

    # Filter to select a subset of rows for action IN
    filter = JSONField(default=dict,
                       blank=True, null=True,
                       help_text='Preselect rows satisfying this condition')

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
            self.filter = formula_evaluation.rename_variable(
                self.filter, old_name, new_name)

        self.save()

    def update_n_rows_selected(self):
        """
        Given an action reset the field n_rows_selected in all conditions

        A second more optimal version could receive the name of a column
        (optional) to process only those that have this name.

        :param column_name: Optional column name to process only those
        conditions that use this column name
        :return: All conditions are updated
        """

        formula = None
        filter = self.conditions.filter(is_filter=True).first()
        if filter:
            formula = filter.formula
            filter.n_rows_selected = pandas_db.num_rows(self.workflow.id,
                                                        formula)
            filter.save()

        self.update_n_rows_selected_for_non_filters(formula)

    def update_n_rows_selected_for_non_filters(self, filter_formula=None):
        """
        Given an action and its filter condition, reset the field n_rows_selected
        in all the non-filter conditions in the action.
        :param action: Action object with the conditions to update
        :param filter_formula: Filter formula to take the conjunction
        :return: All conditions are updated
        """

        # Loop over the non-filter conditions in the action
        for cond in self.conditions.filter(is_filter=False):
            if filter_formula:
                formula = {'condition': 'AND',
                           'not': False,
                           'rules': [cond.formula, filter_formula],
                           'valid': True
                           }
            else:
                formula = cond.formula

            cond.n_rows_selected = \
                pandas_db.num_rows(self.workflow.id, formula)
            cond.save()

    def condition_update_n_rows_selected(self, condition):
        """
        Given a condition update the number of rows
        for which this condition will have true result. In other words,
        we calculate the number of rows for which the condition is true.

        WARNING: If the condition IS NOT a filter, this calculation has to be
        done after the filter condition is applied in order for this number to
        reflect the correct number of rows.

        Conversely, if the condition is a filter, then ALL other conditions need
        to be updated, because the new formula in the filter renders the counts
        in the other conditions obsolete.

        :param action: Action object where the condition is stored
        :param condition: Condition to update the count
        :param filter: Extra condition to use
        :return: field is updated in the condition object
        """

        # See if we are processing a filter or not (in which case needs to be
        # taken into account anyway)
        filter = None
        if not condition.is_filter:
            filter = self.conditions.filter(is_filter=True).first()

        if filter and filter != condition:
            # There is a filter to add to the condition, create a conjunction
            # formula
            formula = {'condition': 'AND',
                       'not': False,
                       'rules': [filter.formula, condition.formula],
                       'valid': True
                       }
        else:
            formula = condition.formula

        condition.n_rows_selected = \
            pandas_db.num_rows(self.workflow.id, formula)
        condition.save()

        if not condition.is_filter:
            # If the condition is not the filter, we are done
            return

        # If the condition given for update is a filter, we need to update all
        # the other conditions in the action
        self.update_n_rows_selected_for_non_filters(
            filter_formula=condition.formula
        )

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
