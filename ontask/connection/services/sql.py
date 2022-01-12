# -*- coding: utf-8 -*-

"""Service functions to handle SQL connections."""

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.connection.services.crud import (
    ConnectionTableAdmin, ConnectionTableSelect,
)
from ontask.core import OperationsColumn


class SQLConnectionTableAdmin(ConnectionTableAdmin):
    """Table to render the SQL admin items."""

    toggle_url_name = 'connection:sqlconn_toggle'

    class Meta(ConnectionTableAdmin.Meta):
        """Define model."""
        model = models.SQLConnection


class SQLConnectionTableSelect(ConnectionTableSelect):
    """Class to render the table of SQL connections."""

    select_url = 'dataops:sqlupload_start'

    class Meta(ConnectionTableSelect.Meta):
        """Define models, fields, sequence and attributes."""

        model = models.SQLConnection


def create_sql_connection_admintable() -> SQLConnectionTableAdmin:
    """Create the table structure with the SQL connections for Admin.

    :return: SQL Connection Table Admin object.
    """
    op_column = OperationsColumn(
        verbose_name=_('Operations'),
        template_file='connection/includes/partial_adminop.html',
        template_context=lambda record: {
            'id': record['id'],
            'edit_url': reverse(
                'connection:sqlconn_edit',
                kwargs={'pk': record['id']}),
            'view_url': reverse(
                'connection:sqlconn_view',
                kwargs={'pk': record['id']}),
            'clone_url': reverse(
                'connection:sqlconn_clone',
                kwargs={'pk': record['id']}),
            'delete_url': reverse(
                'connection:sqlconn_delete',
                kwargs={'pk': record['id']})})
    return SQLConnectionTableAdmin(
        models.SQLConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[(
            'operations', op_column)])


def create_sql_connection_runtable() -> SQLConnectionTableSelect:
    """Create the table structure with the SQL connections for Running.

    :return: SQL Connection Table Run object.
    """
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='connection/includes/partial_select.html',
        template_context=lambda record: {
            'id': record['id'],
            'view_url': reverse(
                'connection:sqlconn_view',
                kwargs={'pk': record['id']})})

    return SQLConnectionTableSelect(
        models.SQLConnection.objects.filter(enabled=True).values(
            'id',
            'name',
            'description_text'),
        orderable=False,
        extra_columns=[('operations', operation_column)])
