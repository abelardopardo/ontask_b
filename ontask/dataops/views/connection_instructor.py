# -*- coding: utf-8 -*-

"""Classes and functions to show connections to regular users."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _
import django_tables2 as tables

from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.core.tables import OperationsColumn
from ontask.models import AthenaConnection, SQLConnection, Workflow


class ConnectionTableRun(tables.Table):
    """Base class to render connections to instructors."""

    class Meta:
        """Define fields, sequence and attributes."""

        fields = ('name', 'description_text')
        sequence = ('name', 'description_text', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'conn-instructor-table',
        }


class AthenaConnectionTableRun(ConnectionTableRun):
    """Class to render the table of Athena connections."""

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a class="js-connection-view" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:athenaconn_view', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta(ConnectionTableRun.Meta):
        """Define models, fields, sequence and attributes."""
        model = AthenaConnection


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


@user_passes_test(is_instructor)
@get_workflow()
def sql_connection_instructor_index(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render a page showing a table with the available SQL connections.

    :param request: HTML request

    :return: HTML response
    """
    del workflow
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_connection_run.html',
        template_context=lambda record: {
            'id': record['id'],
            'run_url': reverse(
                'dataops:sqlupload_start',
                kwargs={'pk': record['id']})})
    table = SQLConnectionTableRun(
        SQLConnection.objects.values(
            'id',
            'name',
            'description_text'),
        orderable=False,
        extra_columns=[('operations', operation_column)])

    return render(
        request,
        'dataops/connections.html',
        {
            'table': table,
            'is_sql': True,
            'title': _('SQL Connections')})


@user_passes_test(is_instructor)
@get_workflow()
def athena_connection_instructor_index(
    request: HttpRequest,
    workflow: Optional[Workflow],
) -> HttpResponse:
    """Render a page showing a table with the available Athena connections.

    :param request: HTML request

    :return: HTML response
    """
    del workflow
    operation_column = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_athenaconn_runop.html',
        template_context=lambda record: {
            'id': record['id'],
            'run_url': reverse(
                'dataops:athenaupload_start',
                kwargs={'pk': record['id']})})
    table = AthenaConnectionTableRun(
        AthenaConnection.objects.values(
            'id',
            'name',
            'description_text'),
        orderable=False,
        extra_columns=[('operations', operation_column)])

    return render(
        request,
        'dataops/connections.html',
        {
            'table': table,
            'is_athena': True,
            'title': _('Athena Connections')})
