# -*- coding: utf-8 -*-

"""Service functions to handle connections."""

from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import create_new_name, models


class ConnectionTableAdmin(tables.Table):
    """Base class for those used to render connection admin items."""

    enabled = tables.BooleanColumn(verbose_name=_('Enabled?'))

    class Meta(object):
        """Define model, fields, sequence and attributes."""

        fields = ('name', 'description_text', 'enabled')
        sequence = ('name', 'description_text', 'enabled', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'connection-admin-table',
        }


class ConnectionTableRun(tables.Table):
    """Base class to render connections to instructors."""

    class Meta(object):
        """Define fields, sequence and attributes."""

        fields = ('name', 'description_text')
        sequence = ('name', 'description_text', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'conn-instructor-table',
        }


def clone(
    request: HttpRequest,
    conn: models.Connection,
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


def delete(
    request: HttpRequest,
    conn: models.Connection,
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


def toggle(
    request: HttpRequest,
    conn: models.Connection,
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
