# -*- coding: utf-8 -*-

"""Classes and functions to view SQL connections."""

from builtins import object

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dataops.forms import SQLConnectionForm
from dataops.models import SQLConnection
from logs.models import Log
from ontask import create_new_name
from ontask.decorators import ajax_required
from ontask.workflow_access import remove_workflow_from_session
from ontask.permissions import is_admin, is_instructor
from ontask.tables import OperationsColumn
from workflow.models import Workflow


class SQLConnectionTableAdmin(tables.Table):
    """Table to render the SQL admin items."""

    operations = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_sqlconn_adminop.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render name as a link."""
        return format_html(
            '<a class="js-sqlconn-edit" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:sqlconn_edit', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta(object):
        """Define model, fields, sequence and attributes."""

        model = SQLConnection

        fields = ('name', 'description_txt')

        sequence = ('name', 'description_txt', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'sqlconn-admin-table',
        }


class SQLConnectionTableRun(tables.Table):
    """Class to render the table of SQL connections."""

    operations = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_sqlconn_runop.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a class="js-sqlconn-view" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:sqlconn_view', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta(object):
        """Define models, fields, sequence and attributes."""

        model = SQLConnection

        fields = ('name', 'description_txt')

        sequence = ('name', 'description_txt', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'sqlconn-instructor-table',
        }


def _save_conn_form(
    request: HttpRequest,
    form: SQLConnectionForm,
    template_name: str,
) -> JsonResponse:
    """Save the connection provided in the form.

    :param request: HTTP request

    :param form: form object with the collected information

    :param template_name: To render the response

    :return: AJAX response
    """
    # Type of event to record
    if form.instance.id:
        event_type = Log.SQL_CONNECTION_EDIT
        is_add = False
    else:
        event_type = Log.SQL_CONNECTION_CREATE
        is_add = True

    # If it is a POST and it is correct
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        conn = form.save()

        # Log the event
        Log.objects.register(
            request.user,
            event_type,
            None,
            {
                'name': conn.name,
                'description': conn.description_txt,
                'conn_type': conn.conn_type,
                'conn_driver': conn.conn_driver,
                'db_user': conn.db_user,
                'db_passwd': _('<PROTECTED>') if conn.db_password else '',
                'db_host': conn.db_host,
                'db_port': conn.db_port,
                'db_name': conn.db_name,
                'db_table': conn.db_table,
            },
        )

        return JsonResponse({'html_redirect': ''})

    # Request is a GET
    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add},
            request=request,
        ),
    })


@user_passes_test(is_admin)
def sqlconnection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the SQL connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)

    return render(
        request,
        'dataops/sql_connections_admin.html',
        {
            'table': SQLConnectionTableAdmin(
                SQLConnection.objects.values(
                    'id',
                    'name',
                    'description_txt'),
                orderable=False)},
    )


@user_passes_test(is_instructor)
def sqlconnection_instructor_index(request: HttpRequest) -> HttpResponse:
    """Render a page showing a table with the SQL connections.

    :param request:

    :return:
    """
    return render(
        request,
        'dataops/sql_connections.html',
        {
            'table': SQLConnectionTableRun(
                SQLConnection.objects.values(
                    'id',
                    'name',
                    'description_txt'),
                orderable=False,
            ),
        },
    )


@user_passes_test(is_instructor)
@ajax_required
def sqlconn_view(request: HttpRequest, pk: int) -> JsonResponse:
    """Show the DB connection in a modal.

    :param request: Request object

    :param pk: Primary key of the SQL connection

    :return: AJAX response
    """
    # Get the connection object
    c_obj = SQLConnection.objects.filter(pk=pk)
    if not c_obj:
        # Connection object not found, go to table of sql connections
        return JsonResponse(
            {'html_redirect': reverse('dataops:sqlconns_admin_index')})

    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_show_sql_connection.html',
            {
                'c_vals': c_obj.values()[0],
                'id': c_obj[0].id,
                'request': request,
            },
        ),
    })


@user_passes_test(is_admin)
@ajax_required
def sqlconn_add(request: HttpRequest) -> JsonResponse:
    """Create a new SQL connection processing the GET/POST requests.

    :param request: Request object

    :return: AJAX response
    """
    # Create the form
    form = SQLConnectionForm(request.POST or None)

    return _save_conn_form(
        request,
        form,
        'dataops/includes/partial_sqlconn_addedit.html')


@user_passes_test(is_admin)
@ajax_required
def sqlconn_edit(request: HttpRequest, pk: int) -> JsonResponse:
    """Respond to the reqeust to edit a SQL CONN object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    # Get the connection
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        return JsonResponse({'html_redirect': reverse('home')})

    # Create the form
    form = SQLConnectionForm(request.POST or None, instance=conn)

    return _save_conn_form(
        request,
        form,
        'dataops/includes/partial_sqlconn_addedit.html')


@user_passes_test(is_admin)
@ajax_required
def sqlconn_clone(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX handshake to clone a SQL connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """
    context = {'pk': pk}  # For rendering

    # Get the connection
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    # Get the name of the connection to clone
    context['cname'] = conn.name

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'dataops/includes/partial_sqlconn_clone.html',
                context,
                request=request),
        })

    # POST REQUEST

    # Proceed to clone the connection
    conn.id = None
    conn.name = create_new_name(conn.name, SQLConnection.objects)
    conn.save()

    # Log the event
    Log.objects.register(
        request.user,
        Log.SQL_CONNECTION_CLONE,
        None,
        {
            'name': conn.name,
            'description': conn.description_txt,
            'conn_type': conn.conn_type,
            'conn_driver': conn.conn_driver,
            'db_user': conn.db_user,
            'db_passwd': _('<PROTECTED>') if conn.db_password else '',
            'db_host': conn.db_host,
            'db_port': conn.db_port,
            'db_name': conn.db_name,
            'db_table': conn.db_table})

    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_admin)
@ajax_required
def sqlconn_delete(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX processor for the delete sql connection operation.

    :param request: AJAX request

    :param pk: primary key for the sql connection

    :return: AJAX response to handle the form
    """
    # Get the connection
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        return JsonResponse({'html_redirect': reverse('home')})

    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.SQL_CONNECTION_DELETE,
            None,
            {'name': conn.name,
             'description': conn.description_txt,
             'conn_type': conn.conn_type,
             'conn_driver': conn.conn_driver,
             'db_user': conn.db_user,
             'db_passwd': _('<PROTECTED>') if conn.db_password else '',
             'db_host': conn.db_host,
             'db_port': conn.db_port,
             'db_name': conn.db_name,
             'db_table': conn.db_table},
        )

        # Perform the delete operation
        conn.delete()

        # In this case, the form is valid anyway
        return JsonResponse({'html_redirect': reverse('home')})

    # This is a GET request
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_sqlconn_delete.html',
            {'sqlconn': conn},
            request=request),
    })
