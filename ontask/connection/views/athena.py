# -*- coding: utf-8 -*-

"""Classes and functions to show connections to regular users."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.connection import forms, services
from ontask.core import (
    ajax_required, get_workflow, is_admin, is_instructor,
    remove_workflow_from_session)
from ontask.core.permissions import UserIsAdmin


class AthenaConnectionAdminIndexView(UserIsAdmin, generic.TemplateView):
    """Show and handle the Athena connections."""

    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.create_athena_connection_admintable()
        context['data_url'] = reverse('connection:athenaconn_add')
        return context


@user_passes_test(is_instructor)
@get_workflow()
def athena_connection_instructor_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow],
) -> http.HttpResponse:
    """Render a page showing a table with the available Athena connections.

    :param request: HTML request
    :param workflow: Current workflow being used
    :return: HTML response
    """
    del workflow
    return render(
        request,
        'connection/index.html',
        {
            'table': services.create_athena_connection_runtable(),
            'is_athena': True,
            'title': _('Athena Connections')})


@user_passes_test(is_instructor)
@ajax_required
def athena_connection_view(
    request: http.HttpRequest,
    pk: int
) -> http.JsonResponse:
    """Show the Athena connection in a modal.

    :param request: Request object
    :param pk: Primary key of the connection element
    :return: AJAX response
    """
    c_obj = models.AthenaConnection.objects.filter(pk=pk).first()
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return http.JsonResponse({
            'html_redirect': reverse('connnection:athenaconns_admin_index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'connection/includes/partial_show.html',
            {'c_vals': c_obj.get_display_dict(), 'id': c_obj.id},
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
        action_url = reverse('connection:athenaconn_add')
    else:
        action_url = reverse('connection:athenaconn_edit', kwargs={'pk': pk})
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
            'connection/includes/partial_addedit.html',
            {
                'form': form,
                'id': form.instance.id,
                'add': is_add,
                'action_url': action_url},
            request=request)})


@user_passes_test(is_admin)
@ajax_required
def athena_connection_clone(
    request: http.HttpRequest,
    pk: int
) -> http.JsonResponse:
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
        reverse('connection:athenaconn_clone', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
@ajax_required
def athena_connection_delete(
    request: http.HttpRequest,
    pk: int
) -> http.JsonResponse:
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
        reverse('connection:athenaconn_delete', kwargs={'pk': conn.id}))


@user_passes_test(is_admin)
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
        reverse('connection:athenaconn_toggle', kwargs={'pk': conn.id}))
