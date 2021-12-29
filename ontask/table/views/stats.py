# -*- coding: utf-8 -*-

"""Implementation of views providing visualisation and stats."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from ontask import models
from ontask.core import ajax_required, get_column, get_workflow, is_instructor
from ontask.table import services


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def stat_column(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.HttpResponse:
    """Render the stat page for a column.

    Render the page with stats and visualizations for the given column The
    page includes the following visualizations: First row: quartile
    information (only for integer and double) V1. Box plot. Only for columns
    of type integer and double. V2. Histogram. For columns of type integer,
    double, string, boolean

    :param request: HTTP request
    :param pk: primary key of the column
    :param workflow: Workflow being manipulated (set by the decorators)
    :param column: Column being manipulated (set by the decorators)
    :return: Render the page
    """
    del pk
    stat_data, __, visualizations = services.get_column_visualization_items(
        workflow, column)

    return render(
        request,
        'table/stat_column.html',
        {
            'column': column,
            'stat_data': stat_data,
            'vis_scripts': [],
            'visualizations': [viz.html_content for viz in visualizations]},
    )


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def stat_column_json(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.JsonResponse:
    """Process JSON GET request to show the column statistics in a modal.

    :param request: HTTP request
    :param pk: Column primary key
    :param workflow: Workflow being manipulated (set by the decorators)
    :param column: Column being manipulated (set by the decorators)
    :return: HTML rendering of the visualization
    """
    del pk
    # Request to see the statistics for a non-key column that belongs to the
    # selected workflow
    stat_data, __, visualizations = services.get_column_visualization_items(
        workflow,
        column)

    # Create the right key/value pair in the result dictionary
    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_column_stats_modal.html',
            context={
                'column': column,
                'stat_data': stat_data,
                'visualizations': [
                    viz.html_content for viz in visualizations],
            },
            request=request),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'views'])
def stat_table_view(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the page with stats and visualizations for a view.

    :param request: HTTP request
    :param pk: View id to use
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: Render the page
    """
    # If the workflow has no data, something went wrong, go back to the
    # workflow details page
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Unable to provide visualisation without data.'))
        return redirect('worflow:detail', workflow.id)

    # Get the key/val pair to select the row (return if not consistent)
    rowselect_key = request.GET.get('key', None)
    rowselect_val = request.GET.get('val', None)
    if bool(rowselect_key) != bool(rowselect_val):
        return render(
            request,
            'error.html',
            {'message': _('Unable to visualize table row')})

    viz_items = services.get_table_visualization_items(
        workflow,
        rowselect_key,
        rowselect_val,
        pk)
    if not viz_items:
        return redirect('home')

    template, context = viz_items
    return render(request, template, context)
