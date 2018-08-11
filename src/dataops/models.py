# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _


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
                                      verbose_name=_('Ready to run'),
                                      null=False,
                                      blank=False)

    # Last time the file was checked (to detect changes)
    executed = models.DateTimeField(
        _('Last execution'),
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


class SQLConnection(models.Model):
    """
    @DynamicAttrs

    Model to represent a connection to a SQL database to be established by
    SQLAlchemy. The parameters for the connection are:

    name
    conn_type
    db_user
    db_password
    db_host
    db_port
    db_name
    db_table
    """

    # Connection name
    name = models.CharField(verbose_name=_('Name'),
                            max_length=2048,
                            null=False,
                            blank=False,
                            unique=True)

    # Description
    description_txt = models.CharField(verbose_name=_('Description'),
                                       max_length=2048,
                                       default='',
                                       blank=True)

    # Connection type: postgresql, mysql, etc.
    conn_type = models.CharField(verbose_name=_('Type'),
                                 max_length=2048,
                                 blank=False,
                                 null=False,
                                 help_text=_('Postgresql, Mysql, etc.'))

    # Connection driver
    conn_driver = models.CharField(
        verbose_name=_('Driver'),
        default='',
        max_length=2048,
        blank=True,
        help_text=_('Driver implementing the DBAPI')
    )

    # User name to connect
    db_user = models.CharField(verbose_name=_('User'),
                               max_length=2048,
                               default='',
                               blank=True)

    # db_password is required (will be asked in run time, but not stored here)
    db_password = models.BooleanField(
        default=False,
        verbose_name=_('Requires password?'),
        null=False,
        blank=False)

    # DB host
    db_host = models.CharField(verbose_name=_('Host'),
                               max_length=2048,
                               default='',
                               blank=True)

    # DB port
    db_port = models.IntegerField(verbose_name=_('Port'),
                                  null=True,
                                  blank=True)

    # DB name
    db_name = models.CharField(max_length=2048,
                               verbose_name=_('DB name'),
                               default='',
                               blank=False,
                               null=False)

    # DB table name
    db_table = models.CharField(max_length=2048,
                                verbose_name=_('Table'),
                                default='',
                                blank=False,
                                null=False)

    def __str__(self):
        return self.name

    class Meta:
        """
        Define the criteria for ordering
        """
        ordering = ('name',)
