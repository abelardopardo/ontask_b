# -*- coding: utf-8 -*-

"""Functions to process the survey run request."""

from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django import http
from django.shortcuts import render
from django.urls import reverse

from ontask import models
from ontask.action.services.manager import ActionManagerBase
from ontask.action.services.manager_factory import action_run_request_factory
from ontask.core import DataTablesServerSidePaging
from ontask.dataops.sql import search_table


def _create_link_to_survey_row(
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


def _create_initial_qs(
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
    if dt_page.order_col is not None:
        order_col_name = columns[dt_page.order_col].name

    # Get the query set (including the filter in the action)
    qs = search_table(
        table_name,
        dt_page.search_value,
        columns_to_search=[col.name for col in columns],
        filter_formula=filter_formula,
        order_col_name=order_col_name,
        order_asc=dt_page.order_dir == 'asc',
    )

    return qs


def _create_table_qsdata(
    action_id: int,
    qs,
    dt_page: DataTablesServerSidePaging,
    columns: List[models.Column],
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
        row[key_idx] = _create_link_to_survey_row(
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


def create_survey_table(
    workflow: models.Workflow,
    action: models.Action,
    dt_page: DataTablesServerSidePaging,
) -> http.JsonResponse:
    """Create the table with the survey entries for instructor.

    :param workflow: Workflow being processed
    :param action: Action representing the survey
    :param dt_page: Data tables server side paging object
    :return : JSon respnse
    """
    columns = [ccpair.column for ccpair in action.column_condition_pair.all()]
    query_set = _create_initial_qs(
        workflow.get_data_frame_table_name(),
        action.get_filter_formula(),
        columns,
        dt_page,
    )

    filtered = len(query_set)

    # Get the subset of the qs to show in the table
    query_set = _create_table_qsdata(
        action.id,
        query_set,
        dt_page,
        columns,
        next(idx for idx, col in enumerate(columns) if col.is_key),
    )

    return http.JsonResponse({
        'draw': dt_page.draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': filtered,
        'data': query_set,
    })


class ActionManagerSurvey(ActionManagerBase):
    """Class to serve running an email action."""

    def __init__(self):
        """Assign initial templates."""
        super().__init__(None)
        self.template = 'action/run_survey.html'

    def process_request(
        self,
        operation_type: str,
        request: http.HttpRequest,
        action: models.Action,
        prev_url: str,
    ) -> http.HttpResponse:
        """Process a GET request."""
        # Render template with active columns.
        return render(
            request,
            self.template,
            {
                'columns': [
                    cc_pair.column
                    for cc_pair in action.column_condition_pair.all()
                    if cc_pair.column.is_active],
                'action': action})


action_run_request_factory.register_processor(
    models.Action.SURVEY,
    ActionManagerSurvey())
