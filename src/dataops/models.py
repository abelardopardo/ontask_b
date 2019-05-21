# -*- coding: utf-8 -*-

"""Models for the plugin registry and the SQL connections."""

from builtins import object

from django.db import models
from django.utils.translation import ugettext_lazy as _

FIELD_LENGTH = 2048
NAME_LENGTH = 256
DESC_LENGTH = 65536


class PluginRegistry(models.Model):
    """Model to store the plugins in the system.

    @DynamicAttrs
    """

    # file in the server
    filename = models.CharField(
        max_length=FIELD_LENGTH,
        blank=False,
        unique=True,
    )

    # Last time the file was checked (to detect changes)
    modified = models.DateTimeField(auto_now=True, null=False)

    # Name provided by the plugin
    name = models.CharField(max_length=NAME_LENGTH, blank=False)

    # Description text
    description_txt = models.CharField(
        max_length=DESC_LENGTH,
        default='',
        blank=True,
    )

    # Boolean stating if the plugin is a model or a transformation
    is_model = models.BooleanField(
        default=False,
        verbose_name=_('Plugin is a model'),
        null=False,
        blank=False,
    )

    # Boolean stating if the column is a unique key
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Ready to run'),
        null=False,
        blank=False,
    )

    # Last time the file was checked (to detect changes)
    executed = models.DateTimeField(
        _('Last verified'),
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self):
        """Render name with field."""
        return self.name

    class Meta(object):
        """Define the criteria for ordering."""

        ordering = ['name']


class SQLConnection(models.Model):
    """Model representing a SQL connection with SQLAlchemy.

    @DynamicAttrs

    The parameters for the connection are:

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
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=FIELD_LENGTH,
        blank=False,
        unique=True)

    # Description
    description_txt = models.CharField(
        verbose_name=_('Description'),
        max_length=FIELD_LENGTH,
        default='',
        blank=True)

    # Connection type: postgresql, mysql, etc.
    conn_type = models.CharField(
        verbose_name=_('Type'),
        max_length=FIELD_LENGTH,
        blank=False,
        help_text=_('Postgresql, Mysql, etc.'))

    # Connection driver
    conn_driver = models.CharField(
        verbose_name=_('Driver'),
        default='',
        max_length=FIELD_LENGTH,
        blank=True,
        help_text=_('Driver implementing the DBAPI'))

    # User name to connect
    db_user = models.CharField(
        verbose_name=_('User'),
        max_length=FIELD_LENGTH,
        default='',
        blank=True)

    # db_password is required (will be asked in run time, but not stored here)
    db_password = models.BooleanField(
        default=False,
        verbose_name=_('Requires password?'),
        null=False,
        blank=False)

    # DB host
    db_host = models.CharField(
        verbose_name=_('Host'),
        max_length=FIELD_LENGTH,
        default='',
        blank=True)

    # DB port
    db_port = models.IntegerField(
        verbose_name=_('Port'),
        null=True,
        blank=True)

    # DB name
    db_name = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name=_('DB name'),
        default='',
        blank=False)

    # DB table name
    db_table = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name=_('Table'),
        default='',
        blank=False)

    def __str__(self):
        """Render with name field."""
        return self.name

    class Meta(object):
        """Define the criteria for ordering."""

        ordering = ['name']
