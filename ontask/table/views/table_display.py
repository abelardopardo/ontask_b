# -*- coding: utf-8 -*-

"""Functions to implement all views related to the table element."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django import http
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask.core.decorators import ajax_required, get_view, get_workflow
from ontask.core.permissions import is_instructor
from ontask import models
from ontask.table import services


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def display(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the page base for displaying the table.

    :param request: HTTP request

    :return: Initial rendering of the page with the table skeleton
    """
    if workflow.nrows == 0:
        # Table is empty, redirect to data upload
        return redirect('dataops:uploadmerge')

    return services.render_table_display_page(
        request,
        workflow,
        None,
        workflow.columns.all(),
        reverse('table:display_ss'),
    )


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_workflow(pf_related='columns')
def display_ss(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Provide the server-side portion to display as a table.

    :param request: HTTP request from dataTables
    :param workflow: Workflog being processed.
    :return: AJAX response
    """
    # If there is not DF, go to workflow details.
    if not workflow.has_table():
        return http.JsonResponse({'error': _('There is no data in the table')})

    return services.render_table_display_server_side(
        request,
        workflow,
        workflow.columns.all(),
        None,
    )


@user_passes_test(is_instructor)
@get_view(pf_related='views')
def display_view(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.HttpResponse:
    """Render the skeleton of the table view.

    :param request: HTTP request
    :param workflow: Workflow current being used
    :param pk: PK of the view to use

    :return: Initial rendering of the page with the table skeleton
    """
    return services.render_table_display_page(
        request,
        workflow,
        view,
        view.columns.all(),
        reverse('table:display_view_ss', kwargs={'pk': view.id}),
    )


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_view(pf_related='views')
def display_view_ss(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Render a view (subset of the table).

    AJAX function to provide a subset of the table for visualisation. The
    subset is defined by the elements in a view

    :param request: HTTP request from dataTables
    :param pk: Primary key of the view to be used
    :param workflow: Workflow being processed
    :param view: View to capture subset of the table
    :return: AJAX response
    """
    return services.render_table_display_server_side(
        request,
        workflow,
        view.columns.all(),
        view.formula,
        view.id)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
def row_delete(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Handle the steps to delete a row in the table.

    :param request: HTTP request
    :param workflow: Workflow being considered.
    :return: AJAX response
    """
    # Get the key/value pair to delete
    row_key = request.GET.get('key')
    row_value = request.GET.get('value')

    # Process the confirmed response
    if request.method == 'POST':
        # if there is no key or value, flag the message and return to table
        # view
        if not row_key or not row_value:
            messages.error(
                request,
                _('Incorrect URL invoked to delete a row'))
            # The response will require going to the table display anyway
            return http.JsonResponse(
                {'html_redirect': reverse('table:display')})


        services.perform_row_delete(workflow, row_key, row_value)

        return http.JsonResponse({'html_redirect': reverse('table:display')})

    # Render the page
    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_row_delete.html',
            {'delete_key': '?key={0}&value={1}'.format(row_key, row_value)},
            request=request),
    })
