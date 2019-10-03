# -*- coding: utf-8 -*-

"""Classes and functions to manage SQL connections."""

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from ontask import create_new_name
from ontask.core.decorators import ajax_required
from ontask.core.permissions import is_admin, is_instructor
from ontask.core.tables import OperationsColumn
from ontask.dataops.forms import SQLConnectionForm
from ontask.dataops.views.connection import (
    ConnectionTableAdmin, ConnectionTableRun, conn_view,
)
from ontask.models import Log, SQLConnection
from ontask.workflow.access import remove_workflow_from_session


class SQLConnectionTableAdmin(ConnectionTableAdmin):
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

    class Meta(ConnectionTableAdmin.Meta):
        """Define model."""
        model = SQLConnection


class SQLConnectionTableRun(ConnectionTableRun):
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

    class Meta(ConnectionTableRun.Meta):
        """Define models, fields, sequence and attributes."""

        model = SQLConnection


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
    is_add = form.instance.id is None
    # If it is a POST and it is correct
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        conn = form.save()
        conn.log(
            request.user,
            Log.SQL_CONNECTION_EDIT if is_add else Log.SQL_CONNECTION_CREATE)
        return JsonResponse({'html_redirect': ''})

    # Request is a GET
    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id, 'add': is_add},
            request=request)})


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
                SQLConnection.objects.values('id', 'name', 'description_text'),
                orderable=False)})


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
                SQLConnection.objects.values('id', 'name', 'description_text'),
                orderable=False)})


@user_passes_test(is_instructor)
@ajax_required
def sqlconn_view(request: HttpRequest, pk: int) -> JsonResponse:
    """Show the DB connection in a modal.

    :param request: Request object

    :param pk: Primary key of the SQL connection

    :return: AJAX response
    """
    # Get the connection object
    c_obj = SQLConnection.objects.filter(pk=pk).values().first()
    if not c_obj:
        # Connection object not found, go to table of sql connections
        return JsonResponse(
            {'html_redirect': reverse('dataops:sqlconns_admin_index')})

    if 'db_password' in c_obj:
        c_obj['db_password'] = '--REMOVED--'
    return conn_view(
        request,
        c_obj,
        SQLConnection._meta,
        'dataops/includes/partial_show_sql_connection.html')


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
    # Get the connection
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'dataops/includes/partial_sqlconn_clone.html',
                {'pk': pk, 'cname': conn.name},
                request=request)})

    # Proceed to clone the connection
    id_old = conn.id
    name_old = conn.name
    conn.id = None
    conn.name = create_new_name(conn.name, SQLConnection.objects)
    conn.save()
    conn.log(
        request.user,
        Log.SQL_CONNECTION_CLONE,
        id_old=id_old,
        name_old=name_old)
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
        conn.log(request.user, Log.SQL_CONNECTION_DELETE)
        conn.delete()
        return JsonResponse({'html_redirect': reverse('home')})

    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_sqlconn_delete.html',
            {'sqlconn': conn},
            request=request)})
