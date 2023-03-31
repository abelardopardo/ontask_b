# -*- coding: utf-8 -*-

"""View objects."""
from typing import Dict, Optional

from django.db import models
from django.db.models import JSONField
from django.utils.translation import ugettext_lazy as _

from ontask.dataops import formula as dataops_formula, sql
from ontask.models.column import Column
from ontask.models.condition import Filter
from ontask.models.common import CreateModifyFields, NameAndDescription
from ontask.models.logs import Log
from ontask.models.workflow import Workflow


class View(NameAndDescription, CreateModifyFields):
    """
    Class to represent different views of the table attached to a workflow.
    It only contains (aside from the basic fields) a formula to filter
    rows, and a subset of the columns in the workflow.

    @DynamicAttrs
    """

    workflow = models.ForeignKey(
        Workflow,
        db_index=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='views')

    # Set of columns for the personalised action IN (subset of the matrix
    # columns
    columns = models.ManyToManyField(
        Column,
        verbose_name=_("Subset of columns to show"),
        related_name='views'
    )

    filter = models.OneToOneField(
        Filter,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name='view')

    # Number of rows allowed by the formula.
    nrows = None

    # Boolean flagging if the formula is empty
    empty_formula = None

    @property
    def formula(self) -> Optional[Filter]:
        """Get the formula value"""
        if self.filter:
            return self.filter.formula

        return None

    @formula.setter
    def formula(self, value: Dict):
        """Setter for the formula field"""
        if self.filter is None:
            raise Exception(_('Incorrect use of view.formula.'))
        self.filter._formula = value

    @property
    def formula_text(self) -> str:
        """Return the text rendering of the formula."""
        if self.filter is None:
            return ''

        return self.filter.formula_text

    @property
    def num_columns(self):
        """Number of columns considered by this view.

        :return: Number of elements in the columns relation
        """
        return self.columns.count()

    @property
    def num_rows(self):
        """Number of rows considered by this view.

        :return: Number of rows resulting from using the formula
        """
        if self.filter:
            return self.filter.selected_count

        return self.workflow.nrows

    @property
    def column_names(self):
        """List of column names.

        :return: List of column names
        """
        return [column.name for column in self.columns.all()]

    @property
    def has_empty_formula(self):
        """Detect if the formula is empty"""
        if self.filter is None:
            return True

        return self.filter.empty_formula

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'columns': [col.name for col in self.columns.all()],
            'formula': self.formula_text,
            'nrows': self.num_rows}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.workflow,
            payload)

    def __str__(self):
        return self.name

    class Meta:
        """Define uniqueness with name in workflow and order by name."""

        unique_together = ('name', 'workflow')
        ordering = ['name']
