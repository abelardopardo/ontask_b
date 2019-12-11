# -*- coding: utf-8 -*-

"""View objects."""
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.dataops import formula, sql
from ontask.models.column import Column
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

    # Formula to select a subset of rows for action IN
    formula = JSONField(
        verbose_name=_("Subset of rows to show"),
        default=dict,
        blank=True,
        null=True,
        help_text=_('Preselect rows satisfying this condition'))

    # Number of rows allowed by the formula.
    nrows = None

    def __str__(self):
        return self.name

    @property
    def num_columns(self):
        """
        Number of columns considered by this view
        :return: Number of elements in the columns relation
        """
        return self.columns.count()

    @property
    def num_rows(self):
        """
        Number of rows considered by this view
        :return: Number of rows resulting from using the formula
        """
        if not self.nrows:
            self.nrows = sql.get_num_rows(
                self.workflow.get_data_frame_table_name(),
                self.formula
            )

        return self.nrows

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'columns': [col.name for col in self.columns.all()],
            'formula': formula.evaluate(
                self.formula,
                formula.EVAL_TXT),
            'nrows': self.nrows}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.workflow,
            payload)

    class Meta:
        """Define uniqueness with name in workflow and order by name."""

        unique_together = ('name', 'workflow')
        ordering = ['name', ]
