# -*- coding: utf-8 -*-

"""Functions to support the display of a table."""
from builtins import next, str
from datetime import datetime
from typing import Any, Optional

from django import http
from django.conf import settings
from django.shortcuts import render, reverse
from django.template.loader import render_to_string
from django.utils.html import escape, urlencode
from django.utils.translation import ugettext_lazy as _
from pytz import timezone

from ontask import models
from ontask.core import DataTablesServerSidePaging
from ontask.dataops import sql
from ontask.table.services.errors import OnTaskTableNoKeyValueError
from ontask.visualizations.plotly import PlotlyHandler


def render_table_display_page(
    request: http.HttpRequest,
    workflow: models.Workflow,
    view: Optional[models.View],
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
        context['columns_show_stat'] = workflow.columns.filter(is_key=False)
    else:
        context['columns'] = None
        context['columns_datatables'] = []

    # If using a view, add it to the context
    context['view'] = view

    return render(request, 'table/display.html', context)


def render_table_display_server_side(
    request,
    workflow,
    columns,
    formula,
    view_id=None,
) -> http.JsonResponse:
    """Render the appropriate subset of the data table.

    Use the search string provided in the UI + the filter (if applicable)
    taken from a view.

    :param request: AJAX request
    :param workflow: workflow object
    :param columns: Subset of columns to consider
    :param formula: Expression to filter rows
    :param view_id: ID of the view restricting the display (if any)
    :return: JSON response
    """
    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return http.JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get columns and names
    column_names = [col.name for col in columns]

    # See if an order has been given.
    order_col_name = None
    if dt_page.order_col:
        # The first column is ops
        order_col_name = column_names[dt_page.order_col - 1]

    qs = sql.search_table(
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
                'table:stat_table_view',
                kwargs={'pk': view_id})
        else:
            stat_url = reverse('table:stat_table')

        # Transform key name and key value into escaped strings
        key_value = escape(row[key_idx])
        ops_string = render_to_string(
            'table/includes/partial_row_ops.html',
            {
                'stat_url': stat_url + '?{0}'.format(urlencode(
                    {'key': key_name, 'val': key_value},
                )),
                'edit_url': reverse('dataops:rowupdate') + '?{0}'.format(
                    urlencode(
                        {'k': key_name,
                         'v': key_value},
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

    return http.JsonResponse({
        'draw': dt_page.draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(qs),
        'data': final_qs,
    })


def perform_row_delete(
    workflow: models.Workflow,
    row_key: str,
    row_value: Any
):
    """Perform the row deletion operation.

    :param workflow: Workflow being considered
    :param row_key: Name of the key column to select the row
    :param row_value: Value of the previous column to select the row.
    :return: Reflected in the workflow
    """
    # if there is no key or value, flag the message and return to table
    # view
    if not row_key or not row_value:
        raise OnTaskTableNoKeyValueError(
            message=_('Incorrect URL invoked to delete a row'))
        # The response will require going to the table display anyway

    # Proceed to delete the row
    sql.delete_row(workflow.get_data_frame_table_name(), (row_key, row_value))

    # Update rowcount
    workflow.nrows -= 1
    workflow.save(update_fields=['nrows'])

    # Update the value of all the conditions in the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for action in workflow.actions.all():
        action.update_n_rows_selected()
