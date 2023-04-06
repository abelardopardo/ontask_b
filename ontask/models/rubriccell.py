"""Rubric Model.

A rubric is modeled as a matrix with M criteria (which are columns in OnTask)
and N level of achievement (possible values in the column). Each cell in the
rubric contains a description, and a feedback text. The model in this file
stores each cell of the rubric and threfore has a reference to a criteria (or
column) a category string, a description string, and a feedback string.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from ontask.models.logs import Log


class RubricCell(models.Model):
    """The cell in a rubric

    - A reference to the action in which it is used

    - A reference to a column (the criteria)

    - A integer with the position of the level of attainment in the column

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

    # Position of the level of attainment
    loa_position = models.IntegerField(
        verbose_name=_('level of attainment'),
        null=False,
        blank=False)

    description_text = models.TextField(
        default='',
        blank=True,
        verbose_name=_('description'))

    feedback_text = models.TextField(
        default='',
        blank=True,
        verbose_name=_('feedback'))

    def __str__(self):
        """Render string."""
        return self.column.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'action': self.action.name,
            'action_id': self.action.id,
            'column': self.column.name,
            'column_id': self.column.id,
            'loa_position': self.loa_position,
            'description': self.description_text,
            'feedback': self.feedback_text}

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

        unique_together = ('action', 'column', 'loa_position')
        ordering = ['column__position', 'loa_position']
