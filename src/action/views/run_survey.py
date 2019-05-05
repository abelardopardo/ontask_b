# -*- coding: utf-8 -*-

"""Views to run a survey by the instructor.

This module implements three views:

- run_survey_ss: Display the rows available for the survey and allow for
  links to run each row individually

- run_survey_row: Run the survey as instructor for a single row
"""
from typing import List, Tuple
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import dataops.sql_query
from action.models import Action
from action.views.serve_survey import serve_survey_row
from core.datatables import DataTablesServerSidePaging
from ontask import OnTaskEmptyWorkflow, OnTaskNoAction, OnTaskNoWorkflow
from ontask.permissions import is_instructor
from workflow.models import Column, Workflow
from ontask.decorators import get_workflow


def run_survey_action(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Render table frame for survey rows (in run_survey_ss).

    Form asking for subject line, email column, etc.
    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action being run
    :return: HTTP response
    """
    # Render template with active columns.
    return render(
        request,
        'action/run_survey.html',
        {
            'columns': [
                cc_pair.column
                for cc_pair in action.column_condition_pair.all()
                if cc_pair.column.is_active],
            'action': action,
        },
    )


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def run_survey_ss(request: HttpRequest, pk: int) -> JsonResponse:
    """Show elements in table that satisfy filter request.

    Serve the AJAX requests to show the elements in the table that satisfy
    the filter and between the given limits.
    :param request:
    :param pk: action id being run
    :return:
    """
    try:
        workflow, action = get_workflow_action(request, pk)
    except Exception as exc:
        return JsonResponse({'error': exc})

    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get columns and the position of the first key
    columns = [ccpair.column for ccpair in action.column_condition_pair.all()]
    key_idx = next(idx for idx, col in enumerate(columns) if col.is_key)

    query_set = create_initial_qs(
        workflow.get_data_frame_table_name(),
        action.get_filter_formula(),
        columns,
        dt_page,
    )

    # Get the subset of the qs to show in the table
    query_set = create_table_qsdata(
        action.id,
        query_set,
        dt_page,
        columns,
        key_idx,
    )

    return JsonResponse({
        'draw': dt_page.draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(query_set),
        'data': query_set,
    })


@user_passes_test(is_instructor)
def run_survey_row(request: HttpRequest, pk: int) -> HttpResponse:
    """Render form for introducing information in a single row.

    Function that runs the action in for a single row. The request
    must have query parameters uatn = key name and uatv = key value to
    perform the lookup.

    :param request:
    :param pk: Action id. It is assumed to be an action In
    :return:
    """
    # Get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect('action:index')

    # If the action is an "out" action, return to index
    if action.is_out:
        return redirect('action:index')

    # Get the parameters
    user_attribute_name = request.GET.get('uatn', 'email')

    return serve_survey_row(request, action, user_attribute_name)


def create_initial_qs(
    table_name,
    filter_formula,
    columns,
    dt_page,
):
    """Obtain the iniital QuerySet to select the right page.

    :param table_name: Workflow to get the table name
    :param filter_formula:
    :param columns: Workflow columns
    :param dt_page: datatables paging information
    :return: query set
    """
    # See if an order column has been given.
    order_col_name = None
    if dt_page.order_col:
        order_col_name = columns[dt_page.order_col].name

    # Get the query set (including the filter in the action)
    qs = dataops.sql_query.search_table(
        table_name,
        dt_page.search_value,
        columns_to_search=[col.name for col in columns],
        filter_formula=filter_formula,
        order_col_name=order_col_name,
        order_asc=dt_page.order_dir == 'asc',
    )

    return qs


def create_table_qsdata(
    action_id: int,
    qs,
    dt_page: DataTablesServerSidePaging,
    columns: List[Column],
    key_idx: int,
) -> List:
    """Select the subset of the qs to be sent as qs data to the JSON request.

    :param action: Action being processed
    :param qs: Query set from where to extract the data
    :param dt_page: Object with DataTable parameters to process the page
    :param column_names: List of column names
    :param key_idx: Index of the key colum
    :return: Query set to return to DataTable JavaScript
    """
    final_qs = []
    item_count = 0
    for row in qs[dt_page.start:dt_page.start + dt_page.length]:
        item_count += 1

        # Render the first element (the key) as the link to the page to update
        # the content.
        row = list(row)
        row[key_idx] = create_link_to_survey_row(
            action_id,
            columns[key_idx].name,
            row[key_idx],
        )

        # Add the row for rendering
        final_qs.append(row)

        if item_count == dt_page.length:
            # We reached the number or requested elements, abandon loop
            break

    return final_qs


def create_link_to_survey_row(
    action_id: int,
    key_name: str,
    key_value,
) -> str:
    """Create the <a> Link element pointing to a survey row form.

    :param action: Action with the survey infroation
    :param key_name:
    :param key_value:
    :return: HTML code with the <a> element
    """
    dst_url = reverse('action:run_survey_row', kwargs={'pk': action_id})
    url_parts = list(urlparse(dst_url))
    query = dict(parse_qs(url_parts[4]))
    query.update({'uatn': key_name, 'uatv': key_value})
    url_parts[4] = urlencode(query)

    return '<a href="{0}">{1}</a>'.format(
        urlunparse(url_parts), key_value,
    )


@login_required
def survey_thanks(request: HttpRequest) -> HttpResponse:
    """Responde simply saying thanks.

    :param request: Http requst
    :return: Http response
    """
    return render(request, 'thanks.html', {})


def get_workflow_action(
    request: HttpRequest,
    pk: int,
) -> Tuple:
    """Get workflow and action for the session.

    Function that returns the action for the given PK and the workflow for
    the session.

    :param request:
    :param pk: Action id.
    :return: (workflow, Action) or Exception
    """
    # Get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        raise OnTaskNoWorkflow(_('Incorrect request. Unable to process.'))

    if workflow.nrows == 0:
        raise OnTaskEmptyWorkflow(_('There is no data in the table'))

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).prefetch_related(
        'column_condition_pair',
    ).first()
    if not action:
        raise OnTaskNoAction(_('Incorrect action requested.'))

    return workflow, action
