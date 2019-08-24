# -*- coding: utf-8 -*-

"""Models for a tuple Action/Column/Condition."""

from django.db import models

from ontask.models import Action, Column, Condition


class ActionColumnConditionTuple(models.Model):
    """Represent tuples (action, column, condition).

    These objects are to:

    1) Represent the collection of columns attached to a regular action

    2) If the action is a survey, see if the question has a condition attached
    to it to decide its presence in the survey.

    @DynamicAttrs
    """

    action = models.ForeignKey(
        Action,
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

    class Meta(object):
        """Define uniqueness with name in workflow and order by name."""

        unique_together = ('action', 'column', 'condition')
        ordering = ['column__position']
