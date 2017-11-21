# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.postgres.fields import JSONField
from django.db import models

from workflow.models import Workflow


class Action(models.Model):
    """
    @DynamicAttrs
    """

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='actions')

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Number or rows selected by the filter in the action (if any)
    n_selected_rows = models.IntegerField(
        verbose_name='Number of rows selected by filter',
        name='n_selected_rows',
        blank=True)

    # Text to be personalised.
    content = models.TextField(
        default='{% comment %}Your action content here{% endcomment %}',
        null=False,
        blank=True)

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(default=False,
                                        verbose_name='URL available to users?',
                                        null=False,
                                        blank=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'workflow')


class Condition(models.Model):
    """
    @DynamicAttrs
    """

    action = models.ForeignKey(Action,
                               db_index=True,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='conditions')

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True)

    formula = JSONField(default=dict, blank=True, null=True)

    # Field to denote if this condition is the filter of an action
    is_filter = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('action', 'name', 'is_filter')
        ordering = ('created', )