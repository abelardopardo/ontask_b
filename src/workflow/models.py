# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models
from django.conf import settings


def get_column_names(workflow):
    return json.loads(workflow.column_names)


def get_column_types(workflow):
    return json.loads(workflow.column_types)


def get_column_areunique(workflow):
    return json.loads(workflow.column_unique)


class Workflow(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    name = models.CharField(max_length=256, blank=False)

    description_text = models.CharField(max_length=512,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Storing a JSON dictionary with (key, value) pairs
    attributes = models.CharField(max_length=65536,
                                  default='',
                                  null=False,
                                  blank=False)

    # Storing the number of rows currently in the data_frame
    nrows = models.IntegerField(verbose_name='Number of rows',
                                default=0,
                                name='nrows',
                                blank=True)

    # Storing the number of rows currently in the data_frame
    ncols = models.IntegerField(verbose_name='Number of columns',
                                default=0,
                                name='ncols',
                                blank=True)

    # Storing a JSON list of with the list of column_names,
    column_names = models.CharField(max_length=65536,
                                    default='',
                                    null=False,
                                    blank=False)

    # Storing a JSON list of column_types
    column_types = models.CharField(max_length=65536,
                                    default='',
                                    null=False,
                                    blank=False)

    # Storing a JSON list of is_unique (or key) booleans
    column_unique = models.CharField(max_length=65536,
                                     default='',
                                     null=False,
                                     blank=False)

    # Storing a JSON object encoding the Operands and operators for jQuery
    # QueryBuilder
    query_builder_ops = models.CharField(max_length=65536,
                                         default='',
                                         null=False,
                                         blank=False)

    # Name of the table storing the data frame
    data_frame_table_name = models.CharField(max_length=1024,
                                             default='',
                                             null=False,
                                             blank=False)

    # shared = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #                                 related_name='shared')
    #
    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')
