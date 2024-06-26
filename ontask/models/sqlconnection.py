"""SQL Connection model."""
from typing import Dict

from django.db import models
from django.utils.translation import gettext_lazy as _
from fernet_fields import EncryptedCharField

from ontask.models.common import CHAR_FIELD_LONG_SIZE
from ontask.models.connection import Connection
from ontask.models.logs import Log


class SQLConnection(Connection):
    """Model representing a SQL connection with SQLAlchemy.

    @DynamicAttrs

    The parameters for the connection are:

    conn_type
    conn_driver
    db_user
    db_password
    db_host
    db_port
    db_name
    db_table
    """

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

    # Username to connect
    db_user = models.CharField(
        verbose_name=_('User'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True)

    # password for the connection
    db_password = EncryptedCharField(
        verbose_name=_('Password'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
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
        blank=False,
        help_text=_('Table name'))

    clone_event = Log.SQL_CONNECTION_CLONE
    create_event = Log.SQL_CONNECTION_CREATE
    delete_event = Log.SQL_CONNECTION_DELETE
    edit_event = Log.SQL_CONNECTION_EDIT
    toggle_event = Log.SQL_CONNECTION_TOGGLE

    @classmethod
    def get(cls, primary_key):
        """Get the object with the given PK."""
        return SQLConnection.objects.get(pk=primary_key)

    def get_display_dict(self) -> Dict:
        """Create dictionary with (verbose_name, value)"""
        d_dict = super().get_display_dict()
        remove_title = self._meta.get_field('db_password').verbose_name.title()
        if remove_title in d_dict:
            d_dict[remove_title] = _('REMOVED')
        return d_dict

    def log(self, user, operation_type: str, **kwargs) -> int:
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
