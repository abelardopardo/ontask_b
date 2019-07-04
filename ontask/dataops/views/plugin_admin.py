# -*- coding: utf-8 -*-

"""Views to administer plugins."""
from typing import Optional

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ontask.core.decorators import ajax_required
from ontask.core.permissions import is_admin, is_instructor
from ontask.dataops.models import Plugin
from ontask.dataops.plugin.plugin_manager import (
    load_plugin, refresh_plugin_data,
)
from ontask.logs.models import Log
from ontask.workflow.access import remove_workflow_from_session
from ontask.workflow.models import Workflow


class PluginAdminTable(tables.Table):
    """Class to render the table with plugins present in the system."""

    description_txt = tables.TemplateColumn(
        verbose_name=_('Description'),
        template_name='dataops/includes/partial_plugin_description.html',
    )

    last_exec = tables.DateTimeColumn(verbose_name=_('Last executed'))

    filename = tables.Column(verbose_name=_('Folder'), empty_values=None)

    num_executions = tables.Column(
        verbose_name=_('Executions'),
        empty_values=[])

    def render_is_verified(self, record):
        """Render is_verified as a tick or the button Diagnose."""
        if record.is_verified:
            return format_html('<span class="true">✔</span>')

        return render_to_string(
            'dataops/includes/partial_plugin_diagnose.html',
            context={'id': record.id},
            request=None)

    def render_is_enabled(self, record):
        """Render the is enabled as a checkbox."""
        return render_to_string(
            'dataops/includes/partial_plugin_enable.html',
            context={'record': record},
            request=None)

    def render_last_exec(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        log_item = Log.objects.filter(
            name=Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '—'
        return log_item.created

    def render_num_executions(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        return Log.objects.filter(
            name=Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).count()

    class Meta(object):
        """Choose fields, sequence and attributes."""

        model = Plugin

        fields = (
            'filename',
            'name',
            'description_txt',
            'is_model',
            'is_verified',
            'is_enabled')

        sequence = (
            'filename',
            'name',
            'description_txt',
            'is_model',
            'is_verified',
            'is_enabled',
            'num_executions',
            'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'plugin-admin-table',
            'th': {'class': 'dt-body-center'},
            'td': {'style': 'vertical-align: middle'}}


@user_passes_test(is_admin)
def plugin_admin(
    request: HttpRequest,
) -> HttpResponse:
    """Show the table of plugins and their status.

    :param request: HTTP Request

    :return:
    """
    remove_workflow_from_session(request)

    # Traverse the plugin folder and refresh the db content.
    refresh_plugin_data(request)

    return render(
        request,
        'dataops/plugin_admin.html',
        {'table': PluginAdminTable(Plugin.objects.all())})


@user_passes_test(is_instructor)
@ajax_required
def diagnose(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Show the diagnostics of a plugin that failed the verification tests.

    :param request: HTML request object

    :param pk: Primary key of the transform element

    :return:
    """
    # Action being used
    plugin = Plugin.objects.filter(id=pk).first()
    if not plugin:
        return JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    pinstance, msgs = load_plugin(plugin.filename)

    # If the new instance is now properly verified, simply redirect to the
    # transform page
    if pinstance:
        plugin.is_verified = True
        plugin.save()
        return JsonResponse({'html_redirect': reverse('dataops:plugin_admin')})

    # Get the diagnostics from the plugin and use it for rendering.
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_diagnostics.html',
            {'diagnostic_table': msgs},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
def moreinfo(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Show the detailed information about a plugin.

    :param request: HTML request object

    :param pk: Primary key of the Plugin element

    :return:
    """
    # Action being used
    plugin = Plugin.objects.filter(id=pk).first()
    if not plugin:
        return JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    pinstance, msgs = load_plugin(plugin.filename)

    # Get the descriptions and show them in the modal
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_plugin_long_description.html',
            {'pinstance': pinstance},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
def plugin_toggle(
    request: HttpRequest,
    pk: int,
) -> JsonResponse:
    """Toggle the field is_enabled of a plugin.

    :param request: HTML request object

    :param pk: Primary key of the Plugin element

    :return:
    """
    plugin_item = Plugin.objects.get(pk=pk)
    if plugin_item.is_verified:
        plugin_item.is_enabled = not plugin_item.is_enabled
        plugin_item.save()
    return JsonResponse({'is_checked': plugin_item.is_enabled})
