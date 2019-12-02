# -*- coding: utf-8 -*-

"""Condition Model."""
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.dataops.formula import EVAL_TXT, evaluate_formula
from ontask.dataops.sql import get_num_rows
from ontask.models.basic import (
    CHAR_FIELD_LONG_SIZE, CHAR_FIELD_MID_SIZE, CreateModifyFields)
from ontask.models.column import Column
from ontask.models.logs import Log


class Condition(CreateModifyFields):
    """Define object to store mainly a formula.

    The object also encodes:
    - is filter or not
    - list of columns in the support of the formula
    - number of rows for which the formula is true

    @DynamicAttrs
    """

    action = models.ForeignKey(
        'Action',
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='conditions')

    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=True,
        verbose_name=_('name'))

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'))

    formula = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('formula'))

    formula_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        null=True,
        verbose_name=_('formula text'))

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name=_('Columns present in this condition'),
        related_name='conditions')

    # Number or rows selected by the expression
    n_rows_selected = models.IntegerField(
        verbose_name=_('Number of rows selected'),
        default=-1,
        name='n_rows_selected',
        blank=False,
        null=False)

    # Field to denote if this condition is the filter of an action
    is_filter = models.BooleanField(default=False)

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
        if not self.formula_text:
            self.formula_text = evaluate_formula(self.formula, EVAL_TXT)
            self.save()
        return self.formula_text

    def __str__(self) -> str:
        """Render string."""
        return self.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'action': self.action.name,
            'formula': self.get_formula_text(),
            'n_rows_selected': self.n_rows_selected,
            'is_filter': self.is_filter,
            'workflow_id': self.action.workflow.id}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.action.workflow,
            payload)

    class Meta:
        """Define unique criteria and ordering.

        The unique criteria here is within the action, the name and being a
        filter. We may choose to name a filter and a condition with the same
        name (no need to restrict it)
        """

        unique_together = ('action', 'name', 'is_filter')
        ordering = ['-is_filter', 'name']
