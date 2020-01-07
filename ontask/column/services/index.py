# -*- coding: utf-8 -*-

"""Functions to create the column details page."""
from typing import Dict

from django.db.models import Q
from django.template.loader import render_to_string

from ontask import models
from ontask.core import DataTablesServerSidePaging


def get_detail_context(workflow: models.Workflow) -> Dict:
    """Create the context to render the details page.

    :param workflow: Workflow being manipulated
    :return: Dictionary to render the details page
    """
    context = {
        'workflow': workflow,
        'table_info': None}
    if workflow.has_table():
        context['table_info'] = {
            'num_rows': workflow.nrows,
            'num_cols': workflow.ncols,
            'num_actions': workflow.actions.count(),
            'num_attributes': len(workflow.attributes)}

    # put the number of key columns in the context
    context['num_key_columns'] = workflow.columns.filter(
        is_key=True,
    ).count()

    # Guarantee that column position is set for backward compatibility
    columns = workflow.columns.all()
    if any(col.position == 0 for col in columns):
        # At least a column has index equal to zero, so reset all of them
        for idx, col in enumerate(columns):
            col.position = idx + 1
            col.save(update_fields=['position'])

    return context


def column_table_server_side(
    dt_page: DataTablesServerSidePaging,
    workflow: models.Workflow,
) -> Dict:
    """Create the server side object to render a page of the table of columns.

    :param dt_page: Table structure for paging a query set.
    :param workflow: Workflow being manipulated
    :return: Dictionary to return to the server to render the sub-page
    """
    # Get the initial set
    qs = workflow.columns.all()
    records_total = qs.count()
    records_filtered = records_total

    # Reorder if required
    if dt_page.order_col:
        col_name = [
            'position',
            'name',
            'description_text',
            'data_type',
            'is_key'][dt_page.order_col]
        if dt_page.order_dir == 'desc':
            col_name = '-' + col_name
        qs = qs.order_by(col_name)

    if dt_page.search_value:
        qs = qs.filter(
            Q(name__icontains=dt_page.search_value)
            | Q(data_type__icontains=dt_page.search_value))
        records_filtered = qs.count()

    # Creating the result
    final_qs = []
    for col in qs[dt_page.start:dt_page.start + dt_page.length]:
        ops_string = render_to_string(
            'column/includes/operations.html',
            {'id': col.id, 'is_key': col.is_key},
        )

        final_qs.append({
            'number': col.position,
            'name': col.name,
            'description': col.description_text,
            'type': col.get_simplified_data_type(),
            'key': '<span class="true">✔</span>' if col.is_key else '',
            'operations': ops_string,
        })

        if len(final_qs) == dt_page.length:
            break

    return {
        'draw': dt_page.draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': final_qs,
    }
