# -*- coding: utf-8 -*-

"""SQL Connection model."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from fernet_fields import EncryptedCharField

from ontask.models.logs import Log
from ontask.models.const import CHAR_FIELD_LONG_SIZE


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
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=False,
        unique=True)

    # Description
    description_text = models.CharField(
        verbose_name=_('Description'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True)

    # Connection type: postgresql, mysql, etc.
    conn_type = models.CharField(
        verbose_name=_('Type'),
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=False,
        help_text=_('Postgresql, Mysql, etc.'))

    # Connection driver
    conn_driver = models.CharField(
        verbose_name=_('Driver'),
        default='',
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=True,
        help_text=_('Driver implementing the DBAPI'))

    # User name to connect
    db_user = models.CharField(
        verbose_name=_('User'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True)

    # db_password is required (will be asked in run time, but not stored here)
    db_password = EncryptedCharField(
        default=False,
        max_length=CHAR_FIELD_LONG_SIZE,
        verbose_name=_('Password (leave empty to enter at execution)'),
        null=True,
        blank=True)

    # DB host
    db_host = models.CharField(
        verbose_name=_('Host'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True)

    # DB port
    db_port = models.IntegerField(
        verbose_name=_('Port'),
        null=True,
        blank=True)

    # DB name
    db_name = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        verbose_name=_('Database name'),
        default='',
        blank=False)

    # DB table name
    db_table = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        verbose_name=_('Database table'),
        default='',
        null=True,
        blank=True)

    def __str__(self):
        """Render with name field."""
        return self.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'conn_type': self.conn_type,
            'conn_driver': self.conn_driver,
            'db_host': self.db_host,
            'db_port': self.db_port,
            'db_name': self.db_name,
            'db_user': self.db_user,
            'db_password': 'SECRET' if self.db_password else '',
            'db_table': self.db_table,
        }

        payload.update(kwargs)
        return Log.objects.register(user, operation_type, None, payload)

    class Meta:
        """Define the criteria for ordering."""

        ordering = ['name']
