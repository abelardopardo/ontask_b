# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from tinymce.models import HTMLField

from workflow.models import Workflow


class Action(models.Model):
    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False)

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Number or rows selected by the filter in the action (if any)
    n_selected_rows = models.IntegerField(
        verbose_name='Number of rows selected by filter',
        name='n_selected_rows',
        blank=True)

    content = HTMLField(
        default='{% comment %} Your action content here{% endcomment %}',
        null=False,
        blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'workflow')


class Condition(models.Model):

    action = models.ForeignKey(Action,
                               db_index=True,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False)

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True)

    formula = models.CharField(max_length=2048, blank=False)

    # Field to denote if this condition is the filter of an action
    is_filter = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('action', 'name')
