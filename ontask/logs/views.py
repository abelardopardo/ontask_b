# -*- coding: utf-8 -*-

"""Views to show logs and log table."""

import json
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import models
from ontask.core import ajax_required, get_workflow, is_instructor
from ontask.logs.services import log_table_server_side


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
                _('Date/Time'),
                _('User'),
                _('Event type')]})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
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
    return http.JsonResponse(log_table_server_side(request, workflow))


@user_passes_test(is_instructor)
@get_workflow()
def view(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """View the content of one of the logs.

    :param request:
    :param pk:
    :return: Http response rendering the view.html
    """
    # Get the log item
    log_item = models.Log.objects.filter(
        pk=pk,
        user=request.user,
        workflow=workflow,
    ).first()

    # If the log item is not there, flag!
    if not log_item:
        messages.error(request, _('Incorrect log number requested'))
        return redirect(reverse('logs:index'))

    return render(
        request,
        'logs/view.html',
        {
            'log_item': log_item,
            'json_pretty': json.dumps(
                log_item.payload,
                sort_keys=True,
                indent=4)})
