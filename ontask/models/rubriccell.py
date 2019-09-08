# -*- coding: utf-8 -*-

"""Rubric Model.

A rubric is modeled as a matrix with M criteria (which are columns in OnTask)
and N level of achievement (possible values in the column). Each cell in the
rubric contains a description, and a feedback text. The model in this file
stores each cell of the rubric and threfore has a reference to a criteria (or
column) a category string, a description string, and a feedback string.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.models.const import CHAR_FIELD_LONG_SIZE, CHAR_FIELD_MID_SIZE


class RubricCell(models.Model):
    """The cell in a rubric

    - A reference to the action in which it is used

    - A reference to a column (the criteria)

    - A text category (which must be one of the possible values allowed in the
      column category) which is the level of attainment.

    - A description text (to define the level of attainment)

    - A feedback text (to provide when a student scores the level of attainment

    @DynamicAttrs
    """

    action = models.ForeignKey(
        'Action',
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='rubric_cells')

    column = models.ForeignKey(
        'Column',
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='rubric_cells')

    category = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        null=False,
        blank=False,
        verbose_name=_('level of attainment'))

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'))

    feedback_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('feedback'))

    def __str__(self):
        """Render string."""
        return self.name

    class Meta:
        """Define unique criteria and ordering.

        The unique criteria here is within the action, the name and being a
        filter. We may choose to name a filter and a condition with the same
        name (no need to restrict it)
        """

        unique_together = ('action', 'column', 'category')
