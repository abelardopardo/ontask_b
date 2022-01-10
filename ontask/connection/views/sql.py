# -*- coding: utf-8 -*-

"""Common functions to handle connections."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.connection import forms, services
from ontask.core import ajax_required, get_workflow, is_admin, is_instructor
from ontask.core.permissions import UserIsAdmin


class SQLConnectionAdminIndexView(UserIsAdmin, generic.TemplateView):
    """Show and handle the SQL connections."""

    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.create_sql_connection_admintable()
        context['data_url'] = reverse('connection:sqlconn_add')
        return context


@user_passes_test(is_instructor)
@get_workflow()
def sql_connection_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render a page showing a table with the available SQL connections.

    :param request: HTML request
    :param workflow: Current workflow being used
    :return: HTML response
    """
    del workflow
    table = services.sql_connection_select_table('dataops:sqlupload_start')
    return render(
        request,
        'connection/index.html',
        {'table': table, 'is_sql': True, 'title': _('SQL Connections')})


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
            'html_redirect': reverse('connection:sqlconns_admin_index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'connection/includes/partial_show.html',
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
        action_url = reverse('connection:sqlconn_add')
    else:
        action_url = reverse('connection:sqlconn_edit', kwargs={'pk': pk})
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
            'connection/includes/partial_addedit.html',
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add,
                'action_url': action_url},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def sql_connection_clone(
    request: http.HttpRequest,
    pk: int
) -> http.JsonResponse:
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
        reverse('connection:sqlconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def sql_connection_delete(
    request: http.HttpRequest,
    pk: int
) -> http.JsonResponse:
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
        reverse('connection:sqlconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def sql_connection_toggle(
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
        reverse('connection:sqlconn_toggle', kwargs={'pk': conn.id}))
