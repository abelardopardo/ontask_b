# -*- coding: utf-8 -*-

"""Service functions to handle athena connections."""
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from ontask import models
from ontask.core import OperationsColumn
from ontask.dataops.services.connections import (
    ConnectionTableAdmin,
    ConnectionTableSelect,
)


class AthenaConnectionTableAdmin(ConnectionTableAdmin):
    """Table to render the Athena admin items."""

    @staticmethod
    def render_name(record):
        """Render name as a link."""
        return format_html(
            '<a class="js-connection-addedit" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:athenaconn_edit', kwargs={'pk': record['id']}),
            record['name'],
        )

    @staticmethod
    def render_enabled(record):
        """Render the boolean to allow changes."""
        return render_to_string(
            'dataops/includes/partial_connection_enable.html',
            {
                'id': record['id'],
                'enabled': record['enabled'],
                'toggle_url': reverse(
                    'dataops:athenaconn_toggle',
                    kwargs={'pk': record['id']})})

    class Meta(ConnectionTableAdmin.Meta):
        """Define model, fields, sequence and attributes."""
        model = models.AthenaConnection


class AthenaConnectionTableSelect(ConnectionTableSelect):
    """Class to render the table of Athena connections."""

    class Meta(ConnectionTableSelect.Meta):
        """Define models, fields, sequence and attributes."""
        model = models.AthenaConnection


def create_athena_connection_admintable() -> AthenaConnectionTableAdmin:
    """Create the table structure with the SQL connections for Admin.

    :return: Athena Connection Table Admin object.
    """
    op_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_adminop.html',
        template_context=lambda record: {
            'id': record['id'],
            'view_url': reverse(
                'dataops:athenaconn_view',
                kwargs={'pk': record['id']}),
            'clone_url': reverse(
                'dataops:athenaconn_clone',
                kwargs={'pk': record['id']}),
            'delete_url': reverse(
                'dataops:athenaconn_delete',
                kwargs={'pk': record['id']})})

    return AthenaConnectionTableAdmin(
        models.AthenaConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[('operations', op_column)])


def create_athena_connection_runtable() -> AthenaConnectionTableSelect:
    """Create the table structure with the SQL connections for Running.

    :return: SQL Connection Table Run object.
    """
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_select.html',
        template_context=lambda record: {
            'id': record['id'],
            'run_url': reverse(
                'dataops:athenaupload_start',
                kwargs={'pk': record['id']}),
            'view_url': reverse(
                'dataops:athenaconn_view',
                kwargs={'pk': record['id']})})
    return AthenaConnectionTableSelect(
        models.AthenaConnection.objects.filter(enabled=True).values(
            'id',
            'name',
            'description_text'),
        orderable=False,
        extra_columns=[('operations', operation_column)])
