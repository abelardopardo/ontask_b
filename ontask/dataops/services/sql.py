
# -*- coding: utf-8 -*-

"""Service functions to handle SQL connections."""
from typing import Dict

from django import http
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from ontask import models
from ontask.core import OperationsColumn
from ontask.dataops.pandas import store_temporary_dataframe, verify_data_frame
from ontask.dataops.services.connections import (
    ConnectionTableAdmin, ConnectionTableRun,
)
from ontask.dataops.services.dataframeupload import load_df_from_sqlconnection
from ontask.models import SQLConnection


class SQLConnectionTableAdmin(ConnectionTableAdmin):
    """Table to render the SQL admin items."""

    def render_name(self, record):
        """Render name as a link."""
        return format_html(
            '<a class="js-connection-addedit" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:sqlconn_edit', kwargs={'pk': record['id']}),
            record['name'],
        )

    def render_enabled(self, record):
        """Render the boolean to allow changes."""
        return render_to_string(
            'dataops/includes/partial_connection_enable.html',
            {
                'id': record['id'],
                'enabled': record['enabled'],
                'toggle_url': reverse(
                    'dataops:sqlconn_toggle',
                    kwargs={'pk': record['id']})})

    class Meta(ConnectionTableAdmin.Meta):
        """Define model."""

        model = SQLConnection


class SQLConnectionTableRun(ConnectionTableRun):
    """Class to render the table of SQL connections."""

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a class="js-connection-view" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:sqlconn_view', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta(ConnectionTableRun.Meta):
        """Define models, fields, sequence and attributes."""

        model = SQLConnection


def create_sql_connection_admintable() -> SQLConnectionTableAdmin:
    """Create the table structure with the SQL connections for Admin.

    :return: SQL Connection Table Admin object.
    """
    op_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_adminop.html',
        template_context=lambda record: {
            'id': record['id'],
            'view_url': reverse(
                'dataops:sqlconn_view',
                kwargs={'pk': record['id']}),
            'clone_url': reverse(
                'dataops:sqlconn_clone',
                kwargs={'pk': record['id']}),
            'delete_url': reverse(
                'dataops:sqlconn_delete',
                kwargs={'pk': record['id']})})
    return SQLConnectionTableAdmin(
        SQLConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[(
            'operations', op_column)])


def create_sql_connection_runtable() -> SQLConnectionTableRun:
    """Create the table structure with the SQL connections for Running.

    :return: SQL Connection Table Run object.
    """
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_run.html',
        template_context=lambda record: {
            'id': record['id'],
            'run_url': reverse(
                'dataops:sqlupload_start',
                kwargs={'pk': record['id']})})
    return SQLConnectionTableRun(
        SQLConnection.objects.filter(enabled=True).values(
            'id',
            'name',
            'description_text'),
        orderable=False,
        extra_columns=[('operations', operation_column)])


def sql_upload_step_one(
    request: http.HttpRequest,
    workflow: models.Workflow,
    conn: SQLConnection,
    run_params: Dict,
):
    """Perform the first step to load a data frame from a SQL connection.

    :param request: Request received.
    :param workflow: Workflow being processed.
    :param conn: Database connection object.
    :param run_params: Dictionary with the additional run parameters.
    :return: Nothing, it creates the new dataframe in the database
    """
    # Process SQL connection using pandas
    data_frame = load_df_from_sqlconnection(conn, run_params)
    # Verify the data frame
    verify_data_frame(data_frame)

    # Store the data frame in the DB.
    # Get frame info with three lists: names, types and is_key
    frame_info = store_temporary_dataframe(
        data_frame,
        workflow)

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    request.session['upload_data'] = {
        'initial_column_names': frame_info[0],
        'column_types': frame_info[1],
        'src_is_key_column': frame_info[2],
        'step_1': reverse(
            'dataops:sqlupload_start',
            kwargs={'pk': conn.id}),
    }
