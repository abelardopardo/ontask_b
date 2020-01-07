# -*- coding: utf-8 -*-

"""Common functions to handle connections."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core import ajax_required, is_admin, is_instructor
from ontask.core.session_ops import remove_workflow_from_session
from ontask.dataops import forms, services


@user_passes_test(is_admin)
def sql_connection_admin_index(request: http.HttpRequest) -> http.HttpResponse:
    """Show and handle the SQL connections.

    :param request: Request
    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)
    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': services.create_sql_connection_admintable(),
            'title': _('SQL Connections'),
            'data_url': reverse('dataops:sqlconn_add')})


@user_passes_test(is_admin)
def athena_connection_admin_index(
    request: http.HttpRequest,
) -> http.HttpResponse:
    """Show and handle the connections.

    :param request: Request
    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)
    return render(
        request,
        'dataops/connections_admin.html',
        {
            'table': services.create_athena_connection_admintable(),
            'title': _('Athena Connections'),
            'data_url': reverse('dataops:athenaconn_add')})


@user_passes_test(is_instructor)
@ajax_required
def sql_connection_view(
    request: http.HttpRequest, 
    pk: int,
) -> http.JsonResponse:
    """Show the SQL connection in a modal.

    :param request: Request object
    :param pk: Primary key of the connection element
    :return: AJAX response
    """
    c_obj = models.SQLConnection.objects.filter(pk=pk).first()
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return http.JsonResponse({
            'html_redirect': reverse('dataops:sqlconns_admin_index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_show.html',
            {'c_vals': c_obj.get_display_dict(), 'id': c_obj.id},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
def athena_connection_view(request: http.HttpRequest, pk: int) -> http.JsonResponse:
    """Show the Athena connection in a modal.

    :param request: Request object
    :param pk: Primary key of the connection element
    :return: AJAX response
    """
    c_obj = models.AthenaConnection.objects.filter(pk=pk).first()
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return http.JsonResponse({
            'html_redirect': reverse('dataops:athenaconns_admin_index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_show.html',
            {'c_vals': c_obj.get_display_dict(), 'id': c_obj.id},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def sql_connection_edit(
    request: http.HttpRequest,
    pk: Optional[int] = None,
) -> http.JsonResponse:
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
            return http.JsonResponse({'html_redirect': reverse('home')})

    form = form_class(request.POST or None, instance=conn)

    # If it is a POST and it is correct
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})
        conn = form.save()
        if is_add:
            conn.log(request.user, conn.create_event)
        else:
            conn.log(request.user, conn.edit_event)
        return http.JsonResponse({'html_redirect': ''})

    # Request is a GET
    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_addedit.html',
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add,
                'action_url': action_url},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def athena_connection_edit(
    request: http.HttpRequest,
    pk: Optional[int] = None,
) -> http.JsonResponse:
    """Respond to the request to create/edit an Athena connection object.

    :param request: HTML request
    :param pk: Primary key
    :return: JSON Response
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
            return http.JsonResponse({'html_redirect': reverse('home')})

    form = form_class(request.POST or None, instance=conn)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})
        conn = form.save()
        if is_add:
            conn.log(request.user, conn.create_event)
        else:
            conn.log(request.user, conn.edit_event)
        return http.JsonResponse({'html_redirect': ''})

    # Request is a GET
    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_connection_addedit.html',
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add,
                'action_url': action_url},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def sql_connection_clone(request: http.HttpRequest, pk: int) -> http.JsonResponse:
    """AJAX handshake to clone an SQL connection.

    :param request: HTTP request
    :param pk: ID of the connection to clone.
    :return: AJAX response
    """
    conn = models.SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return http.JsonResponse({'html_redirect': reverse('home')})

    return services.clone_connection(
        request,
        conn,
        models.SQLConnection.objects,
        reverse('dataops:sqlconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_clone(request: http.HttpRequest, pk: int) -> http.JsonResponse:
    """AJAX handshake to clone an Athena connection.

    :param request: HTTP request
    :param pk: ID of the connection to clone.
    :return: AJAX response
    """
    conn = models.AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return http.JsonResponse({'html_redirect': reverse('home')})

    return services.clone_connection(
        request,
        conn,
        models.AthenaConnection.objects,
        reverse('dataops:athenaconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def sql_connection_delete(request: http.HttpRequest, pk: int) -> http.JsonResponse:
    """AJAX processor for the delete SQL connection operation.

    :param request: AJAX request
    :param pk: primary key for the connection
    :return: AJAX response to handle the form
    """
    conn = models.SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return http.JsonResponse({'html_redirect': reverse('home')})

    return services.delete(
        request,
        conn,
        reverse('dataops:sqlconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_delete(request: http.HttpRequest, pk: int) -> http.JsonResponse:
    """AJAX processor for the delete an Athena connection operation.

    :param request: AJAX request
    :param pk: primary key for the connection
    :return: AJAX response to handle the form
    """
    conn = models.AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return http.JsonResponse({'html_redirect': reverse('home')})

    return services.delete(
        request,
        conn,
        reverse('dataops:athenaconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_instructor)
@ajax_required
def sqlconn_toggle(
    request: http.HttpRequest,
    pk: int,
) -> http.JsonResponse:
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
    request: http.HttpRequest,
    pk: int,
) -> http.JsonResponse:
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
