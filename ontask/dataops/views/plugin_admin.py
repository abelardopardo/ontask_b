# -*- coding: utf-8 -*-

"""Views to administer plugins."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from ontask import OnTaskServiceException, models
from ontask.core import ajax_required, is_admin, is_instructor
from ontask.core.session_ops import remove_workflow_from_session
from ontask.dataops import services


@user_passes_test(is_admin)
def plugin_admin(
    request: http.HttpRequest,
) -> http.HttpResponse:
    """Show the table of plugins and their status.

    :param request: HTTP Request
    :return: Rendered page
    """
    remove_workflow_from_session(request)

    # Traverse the plugin folder and refresh the db content.
    services.refresh_plugin_data(request)
    return render(
        request,
        'dataops/plugin_admin.html',
        {'table': services.PluginAdminTable(models.Plugin.objects.all())})


@user_passes_test(is_instructor)
@ajax_required
def diagnose(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Show the diagnostics of a plugin that failed the verification tests.

    :param request: HTML request object
    :param workflow: Workflow being processed.
    :param pk: Primary key of the transform element
    :return: JSON reponse
    """
    del workflow
    # Action being used
    plugin = models.Plugin.objects.filter(id=pk).first()
    if not plugin:
        return http.JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    try:
        pinstance, msgs = services.load_plugin(plugin.filename)
    except OnTaskServiceException as exc:
        exc.message_to_error(request)
        return http.JsonResponse({
            'html_redirect': reverse('dataops:plugin_admin')})

    # If the new instance is now properly verified, simply redirect to the
    # transform page
    if pinstance:
        plugin.is_verified = True
        plugin.save()
        return http.JsonResponse({
            'html_redirect': reverse('dataops:plugin_admin')})

    # Get the diagnostics from the plugin and use it for rendering.
    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_diagnostics.html',
            {'diagnostic_table': msgs},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
def moreinfo(
    request: http.HttpRequest,
    pk: int,
) -> http.JsonResponse:
    """Show the detailed information about a plugin.

    :param request: HTML request object
    :param pk: Primary key of the Plugin element
    :return: JSON response
    """
    # Action being used
    plugin = models.Plugin.objects.filter(id=pk).first()
    if not plugin:
        return http.JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    try:
        pinstance, msgs = services.load_plugin(plugin.filename)
    except OnTaskServiceException as exc:
        exc.message_to_error(request)
        return http.JsonResponse({
            'html_redirect': reverse('dataops:plugin_admin')})

    # Get the descriptions and show them in the modal
    return http.JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_plugin_long_description.html',
            {'pinstance': pinstance},
            request=request),
    })


@user_passes_test(is_admin)
@ajax_required
def plugin_toggle(
    request: http.HttpRequest,
    pk: int,
) -> http.JsonResponse:
    """Toggle the field is_enabled of a plugin.

    :param request: HTML request object
    :param pk: Primary key of the Plugin element
    :return: JSON Response
    """
    del request
    plugin_item = models.Plugin.objects.filter(pk=pk).first()
    if not plugin_item:
        return http.JsonResponse({})

    if plugin_item.is_verified:
        plugin_item.is_enabled = not plugin_item.is_enabled
        plugin_item.save()
    return http.JsonResponse({'is_checked': plugin_item.is_enabled})
