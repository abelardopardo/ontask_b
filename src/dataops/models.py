# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.shortcuts import redirect

from workflow.models import Workflow, Column


class RowView(models.Model):
    """
    Model to represent a row view, which is a sub-set of columns from the
    workflow to simplify manual data entry through forms.
    """

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 null=False,
                                 blank=False,
                                 related_name='rowview')

    name = models.CharField(max_length=512, blank=False)

    description_text = models.CharField(max_length=2048,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    columns = models.ManyToManyField(Column,
                                     related_name='rowview',
                                     blank=False)

    filter = JSONField(default=dict,
                       blank=True, null=True,
                       help_text='Preselect rows satisfying this condition')

    def get_absolute_url(self):
        """
        Absolute url once there is success updating the element
        :return:
        """
        return redirect('dataops:rowview_edit', kwargs={'pk': self.pk})

    class Meta:
        """
        Define the unique requirement and the ordering of the elements
        """
        unique_together = ('name', 'workflow')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

