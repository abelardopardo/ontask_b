# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import models


class PluginRegistry(models.Model):
    """
    @DynamicAttrs
    """

    # file in the server
    filename = models.CharField(max_length=2048,
                                null=False,
                                blank=False,
                                unique=True)

    # Last time the file was checked (to detect changes)
    modified = models.DateTimeField(auto_now=True, null=False)

    # Name provided by the plugin
    name = models.CharField(max_length=256, blank=False)

    # Description text
    description_txt = models.CharField(max_length=65535,
                                       default='',
                                       blank=True)

    # Number of minimum columns needed to be invocation
    num_column_input_from = models.IntegerField(null=False,
                                                blank=False)

    # Number of maximum columns needed for invocation
    num_column_input_to = models.IntegerField(null=False,
                                              blank=False)
