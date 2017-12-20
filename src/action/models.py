# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import re

import datetime
import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from workflow.models import Workflow, Column


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

    # If the action is to provide information to learners
    is_out = models.BooleanField(default=True,
                                 verbose_name='Action is provide information',
                                 null=False,
                                 blank=False)

    # Boolean that enables the URL to be visible ot the outside.
    serve_enabled = models.BooleanField(default=False,
                                        verbose_name='URL available to users?',
                                        null=False,
                                        blank=False)

    # Validity window for URL availability
    active_from = models.DateTimeField(
        'Action available from',
        blank=True,
        null=True,
        default=None,
    )

    active_to = models.DateTimeField(
        'Action available until',
        blank=True,
        null=True,
        default=None
    )

    #
    # Field for action OUT
    #
    # Text to be personalised for action OUT
    content = models.TextField(
        default='{% comment %}Your action content here{% endcomment %}',
        null=False,
        blank=True)

    #
    # Fields for action IN
    #
    # Set of columns for the personalised action IN (subset of the matrix
    # columns
    columns = models.ManyToManyField(Column,
                                     related_name='actions_in')

    # Filter to select a subset of rows for action IN
    filter = JSONField(default=dict,
                       blank=True, null=True,
                       help_text='Preselect rows satisfying this condition')

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """
        Function to ask if an action is active: the current time is within the
        interval defined by active_from - active_to.
        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not ((self.active_from and now < self.active_from) or
                    (self.active_to and self.active_to < now))

    def rename_variable(self, old_name, new_name):
        """
        Function that renames a variable present in the action content
        :param old_name: Old name of the variable
        :param new_name: New name of the variable
        :return: Updates the current object
        """

        var_use_re = re.compile('{{ (?P<varname>.+?) \}\}')
        new_text = var_use_re.sub(
            lambda m: '{{ ' + \
                      (new_name if m.group('varname') == old_name
                               else m.group('varname')) + ' }}',
            self.content
        )
        self.content = new_text
        self.save()

    class Meta:
        unique_together = ('name', 'workflow')
        ordering = ('name',)


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
        ordering = ('created',)
