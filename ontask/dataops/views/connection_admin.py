# -*- coding: utf-8 -*-

"""Common functions to handle connections"""

from typing import Optional, Type

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import create_new_name
from ontask.core.decorators import ajax_required
from ontask.core.permissions import is_admin, is_instructor
from ontask.core.tables import OperationsColumn
from ontask.dataops.forms import (
    AthenaConnectionForm, ConnectionForm, SQLConnectionForm,
)
from ontask.models import AthenaConnection, Connection, SQLConnection
from ontask.workflow.access import remove_workflow_from_session


class ConnectionTableAdmin(tables.Table):
    """Base class for those used to render connection admin items."""

    enabled = tables.BooleanColumn(verbose_name=_('Enabled?'))

    class Meta:
        """Define model, fields, sequence and attributes."""

        fields = ('name', 'description_text', 'enabled')
        sequence = ('name', 'description_text', 'enabled', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'connection-admin-table',
        }


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


class AthenaConnectionTableAdmin(ConnectionTableAdmin):
    """Table to render the Athena admin items."""

    def render_name(self, record):
        """Render name as a link."""
        return format_html(
            '<a class="js-connection-addedit" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:athenaconn_edit', kwargs={'pk': record['id']}),
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
                    'dataops:athenaconn_toggle',
                    kwargs={'pk': record['id']})})

    class Meta(ConnectionTableAdmin.Meta):
        """Define model, fields, sequence and attributes."""
        model = AthenaConnection


def _save_connection_form(
    request: HttpRequest,
    form: Type[ConnectionForm],
    template_name: str,
    is_add: str,
    action_url: str,
) -> JsonResponse:
    """Save the connection provided in the form.

    :param request: HTTP request

    :param form: form object with the collected information

    :param template_name: To render the response

    :return: AJAX response
    """
    # If it is a POST and it is correct
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})
        conn = form.save()
        if is_add:
            conn.log(request.user, conn.create_event)
        else:
            conn.log(request.user, conn.edit_event)
        return JsonResponse({'html_redirect': ''})

    # Request is a GET
    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add,
                'action_url': action_url},
            request=request)})


def _do_clone(
    request: HttpRequest,
    conn: Type[Connection],
    mgr,
    clone_url: str,
) -> JsonResponse:
    """Finish AJAX handshake to clone a connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """
    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'dataops/includes/partial_connection_clone.html',
                {'pk': conn.id, 'cname': conn.name, 'clone_url': clone_url},
                request=request)})

    # Proceed to clone the connection
    id_old = conn.id
    name_old = conn.name
    conn.id = None
    conn.name = create_new_name(conn.name, mgr)
    conn.save()
    conn.log(
        request.user,
        conn.clone_event,
        id_old=id_old,
        name_old=name_old)
    return JsonResponse({'html_redirect': ''})


def _do_delete(
    request: HttpRequest,
    conn: Type[Connection],
    delete_url: str,
) -> JsonResponse:
    """Finish processing AJAX request for the delete connection operation.

    :param request: AJAX request

    :param pk: primary key for the connection

    :return: AJAX response to handle the form
    """
    if request.method == 'POST':
        conn.log(request.user, conn.delete_event)
        conn.delete()
        return JsonResponse({'html_redirect': ''})

    # This is a GET request
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_delete.html',
            {'name': conn.name, 'delete_url': delete_url},
            request=request),
    })

def _do_toggle(
    request: HttpRequest,
    conn: Type[Connection],
    toggle_url: str,
) -> JsonResponse:
    """Toggle the enable field in the given connection."""
    if not conn:
        messages.error(
            request,
            _('Incorrect invocation of toggle question change function.'))
        return JsonResponse({}, status=404)

    conn.enabled = not conn.enabled
    conn.save()
    conn.log(request.user, conn.toggle_event, enabled=conn.enabled)
    return JsonResponse({'is_checked': conn.enabled, 'toggle_url': toggle_url})


@user_passes_test(is_admin)
def sql_connection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the SQL connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)

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
    table = SQLConnectionTableAdmin(
        SQLConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[(
            'operations', op_column)])

    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': table,
            'title': _('SQL Connections'),
            'data_url': reverse('dataops:sqlconn_add')})


@user_passes_test(is_admin)
def athena_connection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)

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
    table = AthenaConnectionTableAdmin(
        AthenaConnection.objects.values(
            'id',
            'name',
            'description_text',
            'enabled'),
        orderable=False,
        extra_columns=[('operations', op_column)])

    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': table,
            'title': _('Athena Connections'),
            'data_url': reverse('dataops:athenaconn_add')})


@user_passes_test(is_instructor)
@ajax_required
def sql_connection_view(request: HttpRequest, pk: int) -> JsonResponse:
    """Show the SQL connection in a modal.

    :param request: Request object

    :param pk: Primary key of the connection element

    :return: AJAX response
    """
    c_obj = SQLConnection.objects.filter(pk=pk).first()
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return JsonResponse({
            'html_redirect': reverse('dataops:sqlconns_admin_index')})

    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_show.html',
            {'c_vals': c_obj.get_display_dict(), 'id': c_obj.id},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
def athena_connection_view(request: HttpRequest, pk: int) -> JsonResponse:
    """Show the Athena connection in a modal.

    :param request: Request object

    :param pk: Primary key of the connection element

    :return: AJAX response
    """
    c_obj = AthenaConnection.objects.filter(pk=pk).first()
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return JsonResponse({
            'html_redirect': reverse('dataops:athenaconns_admin_index')})

    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_show.html',
            {'c_vals': c_obj.get_display_dict(), 'id': c_obj.id},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def sql_connection_edit(
    request: HttpRequest,
    pk: Optional[int] = None
) -> JsonResponse:
    """Respond to the request to create/edit an SQL connection object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    conn = None
    is_add = pk is None
    if is_add:
        form_class = SQLConnectionForm
        action_url = reverse('dataops:sqlconn_add')
    else:
        form_class = SQLConnectionForm
        action_url = reverse('dataops:sqlconn_edit', kwargs={'pk': pk})
        conn = SQLConnection.objects.filter(pk=pk).first()
        if not conn:
            return JsonResponse({'html_redirect': reverse('home')})

    return _save_connection_form(
        request,
        form_class(request.POST or None, instance=conn),
        'dataops/includes/partial_connection_addedit.html',
        is_add,
        action_url)


@user_passes_test(is_admin)
@ajax_required
def athena_connection_edit(
    request: HttpRequest,
    pk: Optional[int] = None
) -> JsonResponse:
    """Respond to the request to create/edit an Athena connection object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    conn = None
    is_add = pk is None
    if is_add:
        form_class = AthenaConnectionForm
        action_url = reverse('dataops:athenaconn_add')
    else:
        form_class = AthenaConnectionForm
        action_url = reverse('dataops:athenaconn_edit', kwargs={'pk': pk})
        conn = AthenaConnection.objects.filter(pk=pk).first()
        if not conn:
            return JsonResponse({'html_redirect': reverse('home')})

    return _save_connection_form(
        request,
        form_class(request.POST or None, instance=conn),
        'dataops/includes/partial_connection_addedit.html',
        is_add,
        action_url)


@user_passes_test(is_admin)
@ajax_required
def sql_connection_clone(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX handshake to clone an SQL connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """

    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return _do_clone(
        request,
        conn,
        SQLConnection.objects,
        reverse('dataops:sqlconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_clone(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX handshake to clone an Athena connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """
    conn = AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return _do_clone(
        request,
        conn,
        AthenaConnection.objects,
        reverse('dataops:athenaconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def sql_connection_delete(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX processor for the delete SQL connection operation.

    :param request: AJAX request

    :param pk: primary key for the connection

    :return: AJAX response to handle the form
    """
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return _do_delete(
        request,
        conn,
        reverse('dataops:sqlconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_delete(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX processor for the delete an Athena connection operation.

    :param request: AJAX request

    :param pk: primary key for the connection

    :return: AJAX response to handle the form
    """
    conn = AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return _do_delete(
        request,
        conn,
        reverse('dataops:athenaconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_instructor)
@ajax_required
def sqlconn_toggle(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Enable/Disable an SQL connection

    :param request: Request object
    :param pk: Connection PK
    :return: HTML response
    """
    # Check if the workflow is locked
    conn = SQLConnection.objects.filter(pk=pk).first()
    return _do_toggle(
        request,
        conn,
        reverse('dataops:sqlconn_toggle', kwargs={'pk': conn.id}))


@user_passes_test(is_instructor)
@ajax_required
def athenaconn_toggle(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Enable/Disable an Athena connection

    :param request: Request object
    :param pk: Connection PK
    :return: HTML response
    """
    # Check if the workflow is locked
    conn = AthenaConnection.objects.filter(pk=pk).first()
    return _do_toggle(
        request,
        conn,
        reverse('dataops:athenaconn_toggle', kwargs={'pk': conn.id}))
