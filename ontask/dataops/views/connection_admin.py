# -*- coding: utf-8 -*-

"""Common functions to handle connections."""

from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core.decorators import ajax_required
from ontask.core.permissions import is_admin, is_instructor
from ontask.dataops import forms, services
import ontask.dataops.services.athena
import ontask.dataops.services.sql
from ontask.workflow.access import remove_workflow_from_session


@user_passes_test(is_admin)
def sql_connection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the SQL connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)
    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': ontask.dataops.services.sql.create_sql_connection_admintable(),
            'title': _('SQL Connections'),
            'data_url': reverse('dataops:sqlconn_add')})


@user_passes_test(is_admin)
def athena_connection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)
    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': ontask.dataops.services.athena.create_athena_connection_admintable(),
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
    c_obj = models.SQLConnection.objects.filter(pk=pk).first()
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
    c_obj = models.AthenaConnection.objects.filter(pk=pk).first()
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
    pk: Optional[int] = None,
) -> JsonResponse:
    """Respond to the request to create/edit an SQL connection object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    conn = None
    is_add = pk is None
    form_class = forms.SQLConnectionForm
    if is_add:
        action_url = reverse('dataops:sqlconn_add')
    else:
        action_url = reverse('dataops:sqlconn_edit', kwargs={'pk': pk})
        conn = models.SQLConnection.objects.filter(pk=pk).first()
        if not conn:
            return JsonResponse({'html_redirect': reverse('home')})

    return services.save_connection_form(
        request,
        form_class(request.POST or None, instance=conn),
        'dataops/includes/partial_connection_addedit.html',
        is_add,
        action_url)


@user_passes_test(is_admin)
@ajax_required
def athena_connection_edit(
    request: HttpRequest,
    pk: Optional[int] = None,
) -> JsonResponse:
    """Respond to the request to create/edit an Athena connection object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    conn = None
    is_add = pk is None
    form_class = forms.AthenaConnectionForm
    if is_add:
        action_url = reverse('dataops:athenaconn_add')
    else:
        action_url = reverse('dataops:athenaconn_edit', kwargs={'pk': pk})
        conn = models.AthenaConnection.objects.filter(pk=pk).first()
        if not conn:
            return JsonResponse({'html_redirect': reverse('home')})

    return services.save_connection_form(
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
    conn = models.SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return services.clone(
        request,
        conn,
        models.SQLConnection.objects,
        reverse('dataops:sqlconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_clone(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX handshake to clone an Athena connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """
    conn = models.AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return services.clone(
        request,
        conn,
        models.AthenaConnection.objects,
        reverse('dataops:athenaconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def sql_connection_delete(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX processor for the delete SQL connection operation.

    :param request: AJAX request

    :param pk: primary key for the connection

    :return: AJAX response to handle the form
    """
    conn = models.SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return services.delete(
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
    conn = models.AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    return services.delete(
        request,
        conn,
        reverse('dataops:athenaconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_instructor)
@ajax_required
def sqlconn_toggle(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Enable/Disable an SQL connection.

    :param request: Request object
    :param pk: Connection PK
    :return: HTML response
    """
    # Check if the workflow is locked
    conn = models.SQLConnection.objects.filter(pk=pk).first()
    return services.toggle(
        request,
        conn,
        reverse('dataops:sqlconn_toggle', kwargs={'pk': conn.id}))


@user_passes_test(is_instructor)
@ajax_required
def athenaconn_toggle(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Enable/Disable an Athena connection.

    :param request: Request object
    :param pk: Connection PK
    :return: HTML response
    """
    # Check if the workflow is locked
    conn = models.AthenaConnection.objects.filter(pk=pk).first()
    return services.toggle(
        request,
        conn,
        reverse('dataops:athenaconn_toggle', kwargs={'pk': conn.id}))
