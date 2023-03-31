# -*- coding: utf-8 -*-

"""Condition Model."""
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.dataops import formula as dataops_formula, sql
from ontask.models.column import Column
from ontask.models.workflow import Workflow
from ontask.models.common import (
    CHAR_FIELD_LONG_SIZE, CreateModifyFields, NameAndDescription,
)
from ontask.models.logs import Log


class ConditionBase(CreateModifyFields):
    """Object to storing a formula.

    The object also encodes:
    - list of columns in the support of the formula
    - number of rows for which the formula is true

    @DynamicAttrs
    """

    _formula = JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('formula'))

    _formula_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        null=True,
        verbose_name=_('formula text'))

    # Number of rows selected by the expression
    selected_count = models.IntegerField(
        verbose_name=_('Number of rows selected'),
        default=-1,
        name='selected_count',
        blank=False,
        null=False)

    # Boolean flagging if the formula is empty
    empty_formula = None

    def update_fields(self):
        """Update some internal fields when saving an object."""
        # Boolean flagging the formula as empty
        self.empty_formula = dataops_formula.is_empty(self._formula)

        # Text rendering of the formula
        if not self.empty_formula:
            self._formula_text = dataops_formula.evaluate(
                self._formula,
                dataops_formula.EVAL_TXT)
        else:
            self._formula_text = ''

    @property
    def formula(self):
        """Get the formula value"""
        return self._formula

    @formula.setter
    def formula(self, value):
        """Setter for the formula field"""
        self._formula = value

    @property
    def formula_text(self) -> str:
        """Return the text rendering of the formula."""
        return self._formula_text

    def update_selected_count(self, filter_formula=None):
        """Calculate the number of rows for which this condition is true.

        Given a condition update the number of rows for which this condition
        has true result.

        :param filter_formula: Formula provided by another filter condition
        and to take the conjunction with the condition formula.
        :return: Boolean. True if number has changed
        """

        formula = self.formula
        if filter_formula:
            # There is a formula to add to the condition, create a conjunction
            formula = {
                'condition': 'AND',
                'not': False,
                'rules': [filter_formula, self.formula],
                'valid': True,
            }

        old_count = self.selected_count
        self.selected_count = sql.get_num_rows(
            self.workflow.get_data_frame_table_name(),
            formula,
        )

        return old_count != self.selected_count

    class Meta:
        """Make the class abstract."""

        abstract = True


class Condition(NameAndDescription, ConditionBase):
    """Object to storing a Condition that is used in an action.

    @DynamicAttrs
    """

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        default=None,
        on_delete=models.CASCADE,
        related_name='conditions')

    action = models.ForeignKey(
        'Action',
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='conditions')

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name=_('Columns present in this condition'),
        related_name='conditions')

    @property
    def is_filter(self) -> bool:
        """Identify as filter"""
        return False

    def update_fields(self):
        """Update some internal fields when saving an object."""

        super().update_fields()

        self.update_selected_count(
            filter_formula=self.action.get_filter_formula())

    def __str__(self) -> str:
        """Render string."""
        return self.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'action': self.action.name,
            'formula': self.formula_text,
            'selected_count': self.selected_count,
            'workflow_id': self.workflow.id}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.action.workflow,
            payload)

    class Meta:
        """Define unique criteria and ordering.

        The unique criteria here is within the action and the name.
        """

        unique_together = ('action', 'name')
        ordering = ['name']


class Filter(ConditionBase):
    """Object to storing a Filter that is used in an action or a view.

    @DynamicAttrs
    """

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        default=None,
        on_delete=models.CASCADE,
        related_name='filters')

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'),
    )

    # Set of columns that appear in this condition
    columns = models.ManyToManyField(
        Column,
        verbose_name=_('Columns present in this filter'),
        related_name='filters')

    @property
    def is_filter(self) -> bool:
        """Identify as filter"""
        return True

    def update_fields(self):
        """Update some internal fields when saving an object."""

        super().update_fields()
        self.update_selected_count()

    def delete_from_action(self):
        """Remove object from action (and delete if needed)"""
        self.action = None

        if getattr(self, 'view', None) is None:
            super().delete()
            return

        self.save()

    def delete_from_view(self):
        """Remove object from view (and delete if needed)"""
        self.view = None

        if getattr(self, 'action', None) is None:
            super().delete()
            return

        self.save()

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        action = getattr(self, 'action', None)
        payload = {
            'id': self.id,
            'action': action.name if action else '',
            'formula': self.formula_text,
            'selected_count': self.selected_count,
            'workflow_id': self.workflow.id}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.action.workflow,
            payload)

    class Meta:
        """No definitions required here (so far)"""

        pass
