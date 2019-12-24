# -*- coding: utf-8 -*-

"""Service functions to handle SQL connections."""
from typing import Dict

from django import http
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core import OperationsColumn
from ontask.dataops import pandas
from ontask.dataops.services.connections import (
    ConnectionTableAdmin,
    ConnectionTableSelect,
)
from ontask.dataops.services.dataframeupload import load_df_from_sqlconnection


class SQLConnectionTableAdmin(ConnectionTableAdmin):
    """Table to render the SQL admin items."""

    @staticmethod
    def render_enabled(record):
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

        model = models.SQLConnection


class SQLConnectionTableSelect(ConnectionTableSelect):
    """Class to render the table of SQL connections."""

    def __init__(self, *args, **kwargs):
        """Store the select url string to use when rendering name."""
        self.select_url = kwargs.pop('select_url')
        super().__init__(*args, **kwargs)

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a href="{0}">{1}</a>',
            reverse(self.select_url, kwargs={'pk': record['id']}),
            record['name'])

    class Meta(ConnectionTableSelect.Meta):
        """Define models, fields, sequence and attributes."""

        model = models.SQLConnection


def create_sql_connection_admintable() -> SQLConnectionTableAdmin:
    """Create the table structure with the SQL connections for Admin.

    :return: SQL Connection Table Admin object.
    """
    op_column = OperationsColumn(
        verbose_name=_('Operations'),
        template_file='dataops/includes/partial_connection_adminop.html',
        template_context=lambda record: {
            'id': record['id'],
            'edit_url': reverse(
                'dataops:sqlconn_edit',
                kwargs={'pk': record['id']}),
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
        models.SQLConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[(
            'operations', op_column)])


def sql_connection_select_table(
    select_url: str
) -> SQLConnectionTableSelect:
    """Create the table structure with the SQL connections for Running.

    :param select_url: URL to use for the select link in every row
    :return: SQL Connection Table Run object.
    """
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_select.html',
        template_context=lambda record: {
            'id': record['id'],
            'view_url': reverse(
                'dataops:sqlconn_view',
                kwargs={'pk': record['id']})})

    return SQLConnectionTableSelect(
        models.SQLConnection.objects.filter(enabled=True).values(
            'id',
            'name',
            'description_text'),
        select_url=select_url,
        orderable=False,
        extra_columns=[('operations', operation_column)])


def sql_upload_step_one(
    request: http.HttpRequest,
    workflow: models.Workflow,
    conn: models.SQLConnection,
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
    pandas.verify_data_frame(data_frame)

    # Store the data frame in the DB.
    # Get frame info with three lists: names, types and is_key
    frame_info = pandas.store_temporary_dataframe(
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
            'log_upload': models.Log.WORKFLOW_DATA_SQL_UPLOAD,
            'log_merge': models.Log.WORKFLOW_DATA_SQL_MERGE}
