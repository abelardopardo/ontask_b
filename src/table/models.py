# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.postgres.fields import JSONField
from django.db import models

from dataops import pandas_db
from workflow.models import Workflow, Column


class View(models.Model):
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

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512, default='', blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Set of columns for the personalised action IN (subset of the matrix
    # columns
    columns = models.ManyToManyField(
        Column,
        verbose_name="Subset of columns to show",
        related_name='views')

    # Formula to select a subset of rows for action IN
    formula = JSONField(verbose_name="Subset of rows to show",
                        default=dict,
                        blank=True,
                        null=True,
                        help_text='Preselect rows satisfying this condition')

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
        return self.columns.all().count()

    @property
    def num_rows(self):
        """
        Number of rows considered by this view
        :return: Number of rows resulting from using the formula
        """
        if not self.nrows:
            self.nrows = \
                pandas_db.num_rows(self.workflow.id, self.formula)

        return self.nrows

    class Meta:
        """
        Define the criteria of uniqueness with name in workflow and order by
        name
        """
        unique_together = ('name', 'workflow')
        ordering = ('name',)
