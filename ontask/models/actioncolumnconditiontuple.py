# -*- coding: utf-8 -*-

"""Models for a tuple Action/Column/Condition."""

from django.db import models

from ontask.models.column import Column
from ontask.models.condition import Condition
from django.utils.translation import ugettext_lazy as _


class ActionColumnConditionTuple(models.Model):
    """Represent tuples (action, column, condition).

    These objects are to:

    1) Represent the collection of columns attached to a regular action

    2) If the action is a survey, see if the question has a condition attached
    to it to decide its presence in the survey, or if it can be modified

    3) Represent the columns included in a rubric action

    @DynamicAttrs
    """

    action = models.ForeignKey(
        'Action',
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

    # Boolean that enables changes when column is in a survey
    changes_allowed = models.BooleanField(
        default=True,
        verbose_name=_('Allow changes?'),
        null=False,
        blank=False,
    )

    class Meta:
        """Define uniqueness with name in workflow and order by name."""

        unique_together = ('action', 'column', 'condition')
        ordering = ['column__position']
