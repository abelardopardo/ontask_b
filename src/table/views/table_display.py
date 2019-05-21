# -*- coding: utf-8 -*-

"""Functions to implement all views related to the table element."""

from builtins import next, str
from datetime import datetime
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import escape, urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pytz import timezone

from core.datatables import DataTablesServerSidePaging
from dataops.sql import delete_row, search_table
from ontask.decorators import ajax_required, get_view, get_workflow
from ontask.permissions import is_instructor
from table.models import View
from visualizations.plotly import PlotlyHandler
from workflow.models import Workflow


def _render_table_display_page(
    request: HttpRequest,
    workflow: Workflow,
    view: Optional[View],
    columns,
    ajax_url: str,
):
    """Render content of the display page.

    Function to render the content of the display page taking into account
    the columns to show and the AJAX url to use to render the table content.

    :param request: HTTP request

    :param workflow: Workflow object used to access the data frame

    :param view: View to use to render the table (or None)

    :param columns: Columns to display in the page

    :param ajax_url: URL to invoke to populate the table

    :return: HTTP Response
    """
    # Create the initial context
    context = {
        'workflow': workflow,
        'query_builder_ops': workflow.get_query_builder_ops_as_str(),
        'ajax_url': ajax_url,
        'views': workflow.views.all(),
        'no_actions': workflow.actions.count() == 0,
        'vis_scripts': PlotlyHandler.get_engine_scripts(),
    }

    # If there is a DF, add the columns
    if workflow.has_table():
        context['columns'] = columns
        context['column_types'] = str([''] + [
            col.data_type for col in columns])
        context['columns_datatables'] = [{'data': 'Operations'}] + [
            {'data': col.name.replace('.', '\\.')} for col in columns]
        context['stat_columns'] = workflow.columns.filter(is_key=False)
    else:
        context['columns'] = None
        context['columns_datatables'] = []

    # If using a view, add it to the context
    if view:
        context['view'] = view

    return render(request, 'table/display.html', context)


def _render_table_display_data(
    request,
    workflow,
    columns,
    formula,
    view_id=None,
) -> JsonResponse:
    """Render the appropriate subset of the data table.

    Use the search string provided in the UI + the filter (if applicable)
    taken from a view.

    :param request: AJAX request

    :param workflow: workflow object

    :param columns: Subset of columns to consider

    :param formula: Expression to filter rows

    :param view_id: ID of the view restricting the display (if any)

    :return:
    """
    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get columns and names
    column_names = [col.name for col in columns]

    # See if an order has been given.
    order_col_name = None
    if dt_page.order_col:
        # The first column is ops
        order_col_name = column_names[dt_page.order_col - 1]

    qs = search_table(
        workflow.get_data_frame_table_name(),
        dt_page.search_value,
        columns_to_search=column_names,
        filter_formula=formula,
        order_col_name=order_col_name,
        order_asc=dt_page.order_dir == 'asc',
    )

    # Find the first key column
    key_name, key_idx = next(
        ((col.name, idx) for idx, col in enumerate(columns) if col.is_key),
        None)
    key_name = escape(key_name)

    # Post processing + adding operation columns and performing the search
    final_qs = []
    nitems = 0  # For counting the number of elements in the result
    for row in qs[dt_page.start:dt_page.start + dt_page.length]:
        nitems += 1
        new_element = {}
        if view_id:
            stat_url = reverse(
                'table:stat_row_view',
                kwargs={'pk': view_id})
        else:
            stat_url = reverse('table:stat_row')

        # Transform key name and key value into escaped strings
        key_value = escape(row[key_idx])
        ops_string = render_to_string(
            'table/includes/partial_table_ops.html',
            {
                'stat_url': stat_url + '?{0}'.format(urlencode(
                    {'key': key_name, 'val': key_value},
                )),
                'edit_url': reverse('dataops:rowupdate') + '?{0}'.format(
                    urlencode(
                        {'update_key': key_name,
                         'update_val': key_value},
                    )),
                'delete_key': '?{0}'.format(urlencode(
                    {'key': key_name, 'value': key_value},
                )),
                'view_id': view_id,
            },
        )

        # Element to add to the final queryset
        new_element['Operations'] = ops_string
        column_values = [
            rval.astimezone(timezone(
                settings.TIME_ZONE,
            )).strftime('%Y-%m-%d %H:%M:%S  %z')
            if isinstance(rval, datetime) else rval for rval in list(row)
        ]
        new_element.update(zip(column_names, column_values))

        # Create the list of elements to display and add it ot the final QS
        final_qs.append(new_element)

        if nitems == dt_page.length:
            # We reached the number or requested elements, abandon.
            break

    return JsonResponse({
        'draw': dt_page.draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(qs),
        'data': final_qs,
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def display(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the page base for displaying the table.

    :param request: HTTP request

    :return: Initial rendering of the page with the table skeleton
    """
    if workflow.nrows == 0:
        # Table is empty, redirect to data upload
        return redirect('dataops:uploadmerge')

    return _render_table_display_page(
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
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Provide the server-side portion to display as a table.

    :param request: HTTP request from dataTables

    :return: AJAX response
    """
    # If there is not DF, go to workflow details.
    if not workflow.has_table():
        return JsonResponse({'error': _('There is no data in the table')})

    return _render_table_display_data(
        request,
        workflow,
        workflow.columns.all(),
        None,
    )


@user_passes_test(is_instructor)
@get_view(pf_related='views')
def display_view(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """Render the skeleton of the table view.

    :param request: HTTP request

    :param pk: PK of the view to use

    :return: Initial rendering of the page with the table skeleton
    """
    return _render_table_display_page(
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
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> JsonResponse:
    """Render a view (subset of the table).

    AJAX function to provide a subset of the table for visualisation. The
    subset is defined by the elements in a view

    :param request: HTTP request from dataTables

    :param pk: Primary key of the view to be used

    :return: AJAX response
    """
    return _render_table_display_data(
        request,
        workflow,
        view.columns.all(),
        view.formula,
        view.id,
    )


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
def row_delete(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Handle the steps to delete a row in the table.

    :param request: HTTP request

    :return: AJAX response
    """
    # Get the key/value pair to delete
    key = request.GET.get('key')
    row_value = request.GET.get('value')

    # Process the confirmed response
    if request.method == 'POST':
        # if there is no key or value, flag the message and return to table
        # view
        if not key or not row_value:
            messages.error(
                request,
                _('Incorrect URL invoked to delete a row'))
            # The response will require going to the table display anyway
            return JsonResponse({'html_redirect': reverse('table:display')})

        # Proceed to delete the row
        delete_row(workflow.get_data_frame_table_name(), (key, row_value))

        # Update rowcount
        workflow.nrows -= 1
        workflow.save()

        # Update the value of all the conditions in the actions
        # TODO: Explore how to do this asynchronously (or lazy)
        for action in workflow.actions.all():
            action.update_n_rows_selected()

        return JsonResponse({'html_redirect': reverse('table:display')})

    # Render the page
    return JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_row_delete.html',
            {'delete_key': '?key={0}&value={1}'.format(key, row_value)},
            request=request),
    })
