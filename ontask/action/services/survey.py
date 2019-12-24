# -*- coding: utf-8 -*-

"""Functions to process the survey run request."""
from typing import Dict, List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import models
from ontask.action.services.edit_manager import ActionEditManager
from ontask.action.services.run_manager import ActionRunManager
from ontask.core import DataTablesServerSidePaging, OperationsColumn
from ontask.dataops import sql


class ColumnSelectedTable(tables.Table):
    """Table to render the columns selected for a given action in."""

    column_name = tables.Column(
        verbose_name=_('Name'),
        accessor=tables.A('column__name'))  # noqa: Z116
    column_description = tables.Column(  # noqa: Z116
        verbose_name=_('Description (shown to learners)'),
        default='',
        accessor=tables.A('column__description_text'))  # noqa: Z116
    changes_allowed = tables.BooleanColumn(
        verbose_name=_('Allow change?'),
        default=True)
    condition = tables.Column(  # noqa: Z116
        verbose_name=_('Condition'),
        empty_values=[-1],
    )

    # Template to render the extra column created dynamically
    ops_template = 'action/includes/partial_column_selected_operations.html'

    def __init__(self, *args, **kwargs):
        """Store the condition list."""
        self.condition_list = kwargs.pop('condition_list')
        super().__init__(*args, **kwargs)

    def render_condition(
        self,
        record: models.ActionColumnConditionTuple
    ) -> str:
        """Render with template to select condition."""
        cond = record.condition
        return render_to_string(
            'action/includes/partial_column_selected_condition.html',
            {
                'id': record.id,
                'cond_selected': cond.name if cond else None,
                'conditions': self.condition_list,
            })

    @staticmethod
    def render_changes_allowed(
        record: models.ActionColumnConditionTuple
    ) -> str:
        """Render the boolean to allow changes."""
        return render_to_string(
            'action/includes/partial_question_changes_allowed.html',
            {'id': record.id, 'changes_allowed': record.changes_allowed})

    class Meta:
        """Define fields, sequence, attrs and row attrs."""

        fields = (
            'column_id',
            'column_name',
            'column_description',
            'changes_allowed',
            'condition',
            'operations')

        sequence = (
            'operations',
            'column_name',
            'column_description',
            'changes_allowed',
            'condition')

        attrs = {
            'class': 'table table-hover table-bordered',
            'style': 'width: 100%;',
            'id': 'column-selected-table'}

        row_attrs = {
            'class': (
                lambda record:
                'danger' if not record.column.description_text else '')}


def _create_link_to_survey_row(
    action_id: int,
    key_name: str,
    key_value,
) -> str:
    """Create the <a> Link element pointing to a survey row form.

    :param action_id: Action id with the survey information
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
    qs = sql.search_table(
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

    :param action_id: Action id being processed
    :param qs: Query set from where to extract the data
    :param dt_page: Object with DataTable parameters to process the page
    :param columns: List of column
    :param key_idx: Index of the key column
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


class ActionManagerSurvey(ActionEditManager, ActionRunManager):
    """Class to serve running an email action."""

    def extend_edit_context(
        self,
        workflow: models.Workflow,
        action: models.Action,
        context: Dict,
    ):
        """Get the context dictionary to render the GET request.

        :param workflow: Workflow being used
        :param action: Action being used
        :param context: Initial dictionary to extend
        :return: Nothing.
        """
        self.add_conditions(action, context)
        self.add_conditions_to_clone(action, context)
        self.add_columns_show_stats(action, context)

        # All tuples (action, column, condition) to consider
        tuples = action.column_condition_pair.all()

        context.update({
            'column_selected_table': ColumnSelectedTable(
                tuples.filter(column__is_key=False),
                orderable=False,
                extra_columns=[(
                    'operations',
                    OperationsColumn(
                        verbose_name=_('Operations'),
                        template_file=ColumnSelectedTable.ops_template,
                        template_context=lambda record: {
                            'id': record.column.id,
                            'aid': action.id}))],
                condition_list=context['conditions']),
            'columns_to_insert': workflow.columns.exclude(
                column_condition_pair__action=action,
            ).exclude(
                is_key=True,
            ).distinct().order_by('position'),
            'any_empty_description': tuples.filter(
                column__description_text='',
                column__is_key=False,
            ).exists(),
            'key_columns': workflow.get_unique_columns(),
            'key_selected': tuples.filter(column__is_key=True).first(),
            'has_no_key': tuples.filter(column__is_key=False).exists()})

    def process_edit_request(
        self,
        request: http.HttpRequest,
        workflow: models.Workflow,
        action: models.Action
    ) -> http.HttpResponse:
        """Process the action edit request.

        :param request: Http Request received
        :param workflow: Workflow being manipulated
        :param action: Action being used as a survey
        :return: Http response with the right edit template.
        """

        context = self.get_render_context(action)
        try:
            self.extend_edit_context(workflow, action, context)
        except Exception as exc:
            messages.error(request, str(exc))
            return redirect(reverse('action:index'))

        return render(request, self.edit_template, context)

    def process_run_request(
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
            self.run_template,
            {
                'columns': [
                    cc_pair.column
                    for cc_pair in action.column_condition_pair.all()
                    if cc_pair.column.is_active],
                'action': action})
