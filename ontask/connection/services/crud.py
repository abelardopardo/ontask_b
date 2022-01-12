# -*- coding: utf-8 -*-

"""Service functions to handle connections."""
from django import http
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from ontask import create_new_name, models


class ConnectionTableAdmin(tables.Table):
    """Base class to render connection admin table."""

    enabled = tables.BooleanColumn(verbose_name=_('Enabled?'))
    toggle_url_name = None

    def render_enabled(self, record):
        """Render the boolean to allow changes."""
        return render_to_string(
            'connection/includes/partial_enable.html',
            {
                'id': record['id'],
                'enabled': record['enabled'],
                'toggle_url': reverse(
                    self.toggle_url_name,
                    kwargs={'pk': record['id']})})

    class Meta:
        """Define model, fields, sequence and attributes."""

        fields = ('name', 'description_text', 'enabled')
        sequence = ('operations', 'name', 'description_text', 'enabled')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'connection-admin-table',
        }


class ConnectionTableSelect(tables.Table):
    """Base class to render connections to instructors."""

    select_url = None

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a href="{0}">{1}</a>',
            reverse(self.select_url, kwargs={'pk': record['id']}),
            record['name'])

    class Meta:
        """Define fields, sequence and attributes."""

        fields = ('name', 'description_text')
        sequence = ('name', 'description_text', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'conn-instructor-table',
        }


def clone_connection(
    request: http.HttpRequest,
    conn: models.Connection,
    mgr,
) -> http.JsonResponse:
    """Finish AJAX handshake to clone a connection.

    :param request: HTTP request
    :param conn: Connection to clone.
    :param mgr: Manager to handle the right type of connection
    :return: AJAX response
    """
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
    return http.JsonResponse({'html_redirect': ''})
