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

    # Boolean stating if the column is a unique key
    is_verified = models.BooleanField(default=False,
                                      verbose_name='Ready to run',
                                      null=False,
                                      blank=False)

    # Last time the file was checked (to detect changes)
    executed = models.DateTimeField(
        'Last execution',
        blank=True,
        null=True,
        default=None
    )

    def __str__(self):
        return self.name

    class Meta:
        """
        Define the criteria for ordering
        """
        ordering = ('name',)
