# -*- coding: utf-8 -*-

"""Implementation of views providing visualisation and stats."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from ontask.dataops.pandas import get_column_statistics, load_table
from ontask.dataops.sql.row_queries import get_rows
from ontask.core.decorators import ajax_required, get_column, get_workflow
from ontask.core.permissions import is_instructor
from ontask.visualizations.plotly import PlotlyBoxPlot, PlotlyColumnHistogram
from ontask.workflow.models import Column, Workflow

VISUALIZATION_WIDTH = 468
VISUALIZATION_HEIGHT = 250


def _get_column_visualisations(
    column,
    col_data,
    vis_scripts,
    viz_id='',
    single_val=None,
    context=None,
):
    """Create a column visualization.

    Given a column object and a dataframe, create the visualisations for this
    column. The list vis_scripts is modified to include the scripts to
    include in the HTML page. If single_val is not None, its position in the
    visualisation is marked (place individual value in population measure.

    :param column: Column element to visualize

    :param col_data: Data in the column (extracted from the data frame)

    :param viz_id: String to use to label the visualization

    :param vis_scripts: Collection of visualisation scripts needed in HTML

    :param single_val: Mark a specific value (or None)

    :param context: Dictionary to pass to the rendering

    :return:
    """
    # Result to return
    visualizations = []

    # Initialize the context properly
    if context is None:
        context = {}

    # Create V1 if data type is integer or real
    if column.data_type == 'integer' or column.data_type == 'double':

        # Propagate the id if given
        if viz_id:
            context['id'] = viz_id + '_boxplot'

        if single_val is not None:
            context['individual_value'] = single_val
        v1 = PlotlyBoxPlot(
            data=col_data,
            context=context)
        v1.get_engine_scripts(vis_scripts)
        visualizations.append(v1)

    # Create V2
    # Propagate the id if given
    if viz_id:
        context['id'] = viz_id + '_histogram'

    if single_val is not None:
        context['individual_value'] = single_val
    v2 = PlotlyColumnHistogram(
        data=col_data,
        context=context)
    v2.get_engine_scripts(vis_scripts)
    visualizations.append(v2)

    return visualizations


def _get_column_visualization_items(
    workflow,
    column,
    max_width=VISUALIZATION_WIDTH,
    max_height=VISUALIZATION_HEIGHT,
):
    """Get the visualization items (scripts and HTML) for a column.

    :param workflow: Workflow being processed

    :param column: Column requested

    :param max_width: Maximum width attribute in pixels

    :param max_width: Maximum height attribute in pixels

    :return: Tuple stat_data with descriptive stats, visualization scripts and
    visualization HTML
    """
    # Get the dataframe
    df = load_table(workflow.get_data_frame_table_name())

    # Extract the data to show at the top of the page
    stat_data = get_column_statistics(df[column.name])

    vis_scripts = []
    visualizations = _get_column_visualisations(
        column,
        df[[column.name]],
        vis_scripts,
        context={
            'style': 'max-width:{0}px; max-height:{1}px;'.format(
                max_width,
                max_height,
            ) + 'display:inline-block;',
        },
    )

    return stat_data, vis_scripts, visualizations


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def stat_column(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Render the stat page for a column.

    Render the page with stats and visualizations for the given column The
    page includes the following visualizations: First row: quartile
    information (only for integer and double) V1. Box plot. Only for columns
    of type integer and double. V2. Histogram. For columns of type integer,
    double, string, boolean

    :param request: HTTP request

    :param pk: primary key of the column

    :return: Render the page
    """
    stat_data, vis_scripts, visualizations = _get_column_visualization_items(
        workflow, column)

    return render(
        request,
        'table/stat_column.html',
        {
            'column': column,
            'stat_data': stat_data,
            'vis_scripts': vis_scripts,
            'visualizations': [viz.html_content for viz in visualizations]},
    )


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def stat_column_json(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
    """Process JSON GET request to show the column statistics in a modal.

    :param request: HTTP request

    :param pk: Column primary key

    :return: HTML rendering of the visualization
    """
    # Request to see the statistics for a non-key column that belongs to the
    # selected workflow

    stat_data, __, visualizations = _get_column_visualization_items(
        workflow,
        column,
        max_height=VISUALIZATION_HEIGHT,
        max_width=VISUALIZATION_WIDTH)

    # Create the right key/value pair in the result dictionary
    return JsonResponse({
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
def stat_row_view(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render stats for a row.

    Render the page with stats and visualizations for a row in the table and
    a view (subset of columns). The request must include key and value to get
    the right row. In principle, there is a visualisation for each row.

    :param request: HTTP request

    :param pk: View id to use

    :return: Render the page
    """
    # If there is no workflow object, go back to the index
    # Get the pair key,value to fetch the row from the table
    update_key = request.GET.get('key')
    update_val = request.GET.get('val')

    if not update_key or not update_val:
        # Malformed request
        return render(
            request,
            'error.html',
            {'message': _('Unable to visualize table row')})

    # If a view is given, filter the columns
    columns_to_view = workflow.columns.all()
    column_names = workflow.get_column_names()
    if pk:
        view = workflow.views.filter(pk=pk).first()
        if not view:
            # View not found. Redirect to home
            return redirect('home')
        columns_to_view = view.columns.all()
        column_names = [col.name for col in columns_to_view]

        df = load_table(
            workflow.get_data_frame_table_name(),
            column_names,
            view.formula)
    else:
        # No view given, fetch the entire data frame
        df = load_table(workflow.get_data_frame_table_name())

    # Get the row from the table
    row = get_rows(
        workflow.get_data_frame_table_name(),
        column_names=column_names,
        filter_pairs={update_key: update_val},
    ).fetchone()

    vis_scripts = []
    visualizations = []
    context = {'style': 'width:400px; height:225px;'}
    for idx, column in enumerate(columns_to_view):

        # Skip primary keys (no point to represent any of them)
        if column.is_key:
            continue

        # Add the title and surrounding container
        visualizations.append('<h4>' + column.name + '</h4>')
        # If all values are empty, no need to proceed
        if all(not col for col in df[column.name]):
            visualizations.append(
                '<p>' + _('No values in this column') + '</p><hr/>')
            continue

        if row[column.name] is None or row[column.name] == '':
            visualizations.append(
                '<p class="alert-warning">'
                + _('No value for this student in this column')
                + '</p>',
            )

        visualizations.append('<div style="display: inline-flex;">')

        col_viz = _get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts=vis_scripts,
            viz_id='column_{0}'.format(idx),
            single_val=row[column.name],
            context=context)

        visualizations.extend([viz.html_content for viz in col_viz])
        visualizations.append('</div><hr/>')

    return render(
        request,
        'table/stat_row.html',
        {
            'value': update_val,
            'vis_scripts': vis_scripts,
            'visualizations': visualizations})


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'views'])
def stat_table_view(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the page with stats and visualizations for a view.

    :param request: HTTP request

    :param pk: View id to use

    :return: Render the page
    """
    # If the workflow has no data, something went wrong, go back to the
    # workflow details page
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Unable to provide visualisation without data.'))
        return redirect('worflow:detail', workflow.id)

    # If a view is given, filter the columns
    view = None
    if pk:
        view = workflow.views.filter(pk=pk).first()
        if not view:
            # View not found. Redirect to workflow detail
            return redirect('home')
        columns_to_view = view.columns.filter(is_key=False)

        df = load_table(
            workflow.get_data_frame_table_name(),
            [col.name for col in columns_to_view],
            view.formula)
    else:
        # No view given, fetch the entire data frame
        columns_to_view = workflow.columns.filter(is_key=False)
        df = load_table(workflow.get_data_frame_table_name())

    vis_scripts = []
    visualizations = []
    idx = -1
    context = {'style': 'width:400px; height:225px;'}
    for column in columns_to_view:
        idx += 1

        # Skip primary keys (no point to represent any of them)
        if column.is_key:
            continue

        # Add the title and surrounding container
        visualizations.append('<h4>' + column.name + '</h4>')
        # If all values are empty, no need to proceed
        if all(not col_data for col_data in df[column.name]):
            visualizations.append('<p>No values in this column</p><hr/>')
            continue

        visualizations.append('<div style="display: inline-flex;">')

        column_viz = _get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts=vis_scripts,
            viz_id='column_{0}'.format(idx),
            context=context)

        visualizations.extend([vis.html_content for vis in column_viz])
        visualizations.append('</div><hr/>')

    return render(
        request,
        'table/stat_view.html',
        {'view': view,
         'vis_scripts': vis_scripts,
         'visualizations': visualizations})
