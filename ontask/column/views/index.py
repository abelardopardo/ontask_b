# -*- coding: utf-8 -*-

"""Functions to render the table of columns."""
from typing import Optional

from django import http
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ontask import models
from ontask.column import services
from ontask.core import (
    DataTablesServerSidePaging, ajax_required, check_workflow, get_workflow,
    is_instructor,
)


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'shared'])
def index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow],
) -> http.HttpResponse:
    """Http request to serve the details page for the workflow.

    :param request: HTTP Request
    :param workflow: Workflow being manipulated
    :return: Http response with the page rendering
    """
    # Safety check for consistency (only in development)
    if settings.DEBUG:
        check_workflow(workflow)

    return render(
        request,
        'column/detail.html',
        services.get_detail_context(workflow))


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_POST
@get_workflow(pf_related='columns')
def index_ss(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Render the server side page for the table of columns.

    Given the workflow id and the request, return to DataTable the proper
    list of columns to be rendered.

    :param request: Http request received from DataTable
    :param workflow: Workflow being manipulated.
    :return: Data to visualize in the table
    """
    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return http.JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    return http.JsonResponse(
        services.column_table_server_side(dt_page, workflow))
