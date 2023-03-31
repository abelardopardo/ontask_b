# -*- coding: utf-8 -*-

"""Views to show logs and log table."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status

from ontask import models
from ontask.core import ajax_required, get_workflow, is_instructor
from ontask.logs import services


@user_passes_test(is_instructor)
@get_workflow()
def display(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the table frame for the logs.

    :param request: Http request
    :param workflow: workflow
    :return: Http response
    """
    # Render the page with the table
    return render(
        request,
        'logs/display.html',
        {
            'workflow': workflow,
            'column_names': [
                _('ID'),
                _('Event type'),
                _('Date/Time'),
                _('User')]})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_POST
@get_workflow(pf_related='logs')
def display_ss(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Return the subset of logs to include in a table page.

    :param request: Http Request
    :param workflow: Workflow being manipulated.
    :return: JSON response
    """
    # Render the page with the table
    return http.JsonResponse(services.log_table_server_side(request, workflow))


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def modal_view(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """View the content of one of the logs in a modal.

    :param request: Http Request received
    :param pk: Primary key of the log to view
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: JSON response to render in a modal
    """
    # Get the log item
    log_item = workflow.logs.filter(pk=pk, user=request.user).first()

    # If the log item is not there, flag!
    if not log_item:
        messages.error(request, _('Incorrect log number requested'))
        return http.JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    return http.JsonResponse({
        'html_form': render_to_string(
            'logs/includes/partial_show.html',
            {'log_item': log_item, 'c_vals': log_item.payload},
            request=request)})


@user_passes_test(is_instructor)
@get_workflow()
def page_view(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """View the content of one of the logs.

    :param request: Http Request received
    :param pk: Primary key of the log to view
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: Http response rendering the view.html
    """
    # Get the log item
    log_item = workflow.logs.filter(pk=pk, user=request.user).first()

    # If the log item is not there, flag!
    if not log_item:
        messages.error(request, _('Incorrect log number requested'))
        return redirect(reverse('logs:index'))

    return render(
        request,
        'logs/view.html',
        {'log_item': log_item, 'c_vals': log_item.payload})


@user_passes_test(is_instructor)
@get_workflow()
def export(
    request: http.HttpRequest,
    wid: int,
    workflow: models.Workflow
) -> http.HttpResponse:
    """Export the logs from the given workflow.

    :param request: HTML request
    :param wid: pk of the workflow to export
    :param workflow: Workflow being manipulated
    :return: Return a CSV download of the logs
    """
    del wid
    dataset = services.LogResource().export(
        workflow.logs.filter(user=request.user))

    # Create the response as a csv download
    response = http.HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs.csv"'

    return response
