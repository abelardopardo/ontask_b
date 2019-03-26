# -*- coding: utf-8 -*-
"""
Implementation of views providing visualisation and stats
"""

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext as _

from dataops import pandas_db
from dataops.pandas_db import load_from_db, get_column_stats_from_df
from ontask.permissions import is_instructor
from table.models import View
from visualizations.plotly import PlotlyBoxPlot, PlotlyColumnHistogram
from workflow.models import Column
from workflow.ops import get_workflow


def get_column_visualisations(column, col_data, vis_scripts,
                              id='', single_val=None, context=None):
    """
    Given a column object and a dataframe, create the visualisations for
    this column. The list vis_scripts is modified to include the scripts to
    include in the HTML page. If single_val is not None, its position in
    the visualisation is marked (place individual value in population
    measure.
    :param column: Column element to visualize
    :param col_data: Data in the column (extracted from the data frame)
    :param id: String to use to label the visualization
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
        if id:
            context['id'] = id + '_boxplot'

        if single_val is not None:
            context['individual_value'] = single_val
        v1 = PlotlyBoxPlot(data=col_data,
                           context=context)
        v1.get_engine_scripts(vis_scripts)
        visualizations.append(v1)

    # Create V2
    # Propagate the id if given
    if id:
        context['id'] = id + '_histogram'

    if single_val is not None:
        context['individual_value'] = single_val
    v2 = PlotlyColumnHistogram(data=col_data,
                               context=context)
    v2.get_engine_scripts(vis_scripts)
    visualizations.append(v2)

    return visualizations


def get_row_visualisations(request, view_id=None):
    # If there is no workflow object, go back to the index
    workflow = get_workflow(request)
    if not workflow:
        return redirect('home')

    # If the workflow has no data, something went wrong, go back to the
    # workflow details page
    if workflow.nrows == 0:
        return redirect('worflow:detail', workflow.id)

    # Get the pair key,value to fetch the row from the table
    update_key = request.GET.get('key', None)
    update_val = request.GET.get('val', None)

    if not update_key or not update_val:
        # Malformed request
        return render(request, 'error.html',
                      {'message': _('Unable to visualize table row')})

    # If a view is given, filter the columns
    columns_to_view = workflow.columns.all()
    column_names = workflow.get_column_names()
    if view_id:
        try:
            view = View.objects.get(pk=view_id)
        except ObjectDoesNotExist:
            # View not found. Redirect to workflow detail
            return redirect('workflow:detail', workflow.id)
        columns_to_view = view.columns.all()
        column_names = [c.name for c in columns_to_view]

        df = pandas_db.load_from_db(workflow.get_data_frame_table_name(),
                                    column_names,
                                    view.formula)
    else:
        # No view given, fetch the entire data frame
        df = pandas_db.load_from_db(workflow.get_data_frame_table_name())

    # Get the rows from the table
    row = pandas_db.execute_select_on_table(
        workflow.get_data_frame_table_name(),
        [update_key],
        [update_val],
        column_names
    )[0]

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
        if all([not x for x in df[column.name]]):
            visualizations.append("<p>" +
                                  _('No values in this column') +
                                  "</p><hr/>")
            continue

        if row[idx] is None or row[idx] == '':
            visualizations.append(
                '<p class="alert-warning">' +
                _('No value for this student in this column') + '</p>'
            )

        visualizations.append(
            '<div style="display: inline-flex;">'
        )

        v = get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts=vis_scripts,
            id='column_{0}'.format(idx),
            single_val=row[idx],
            context=context)

        visualizations.extend([x.html_content for x in v])
        visualizations.append('</div><hr/>')

    return render(request,
                  'table/stat_row.html',
                  {'value': update_val,
                   'vis_scripts': vis_scripts,
                   'visualizations': visualizations})


def get_view_visualisations(request, view_id=None):
    """
    Function that returns the visualisations for a view (or the entire table)
    :param request: HTTP request
    :param view_id: View id being used
    :return: HTTP response

    TODO: Review this function and get_row_visualisation because there is a
    significant overlap.
    """
    # If there is no workflow object, go back to the index
    workflow = get_workflow(request)
    if not workflow:
        return redirect('home')

    # If the workflow has no data, something went wrong, go back to the
    # workflow details page
    if workflow.nrows == 0:
        messages.error(request,
                       _('Unable to provide visualisation without data.'))
        return redirect('worflow:detail', workflow.id)

    # If a view is given, filter the columns
    columns_to_view = workflow.columns.all()
    view = None
    if view_id:
        try:
            view = View.objects.get(pk=view_id)
        except ObjectDoesNotExist:
            # View not found. Redirect to workflow detail
            return redirect('workflow:detail', workflow.id)
        columns_to_view = view.columns.all()

        df = pandas_db.load_from_db(workflow.get_data_frame_table_name(),
                                    [x.name for x in columns_to_view],
                                    view.formula)
    else:
        # No view given, fetch the entire data frame
        df = pandas_db.load_from_db(workflow.get_data_frame_table_name())

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
        if all([not x for x in df[column.name]]):
            visualizations.append("<p>No values in this column</p><hr/>")
            continue

        visualizations.append(
            '<div style="display: inline-flex;">'
        )

        v = get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts=vis_scripts,
            id='column_{0}'.format(idx),
            context=context)

        visualizations.extend([x.html_content for x in v])
        visualizations.append('</div><hr/>')

    return render(request,
                  'table/stat_view.html',
                  {'view': view,
                   'vis_scripts': vis_scripts,
                   'visualizations': visualizations})


def get_column_visualization_items(workflow,
                                   column,
                                   max_width=800,
                                   max_height=450):
    """
    Get the visualization items (scripts and HTML) for a column
    :param workflow: Workflow being processed
    :param column: Column requested
    :param max_width: Maximum width attribute in pixels
    :param max_width: Maximum height attribute in pixels
    :return: Tuple stat_data with descriptive stats, visualization scripts and
    visualization HTML
    """
    # Get the dataframe
    df = load_from_db(workflow.get_data_frame_table_name())

    # Extract the data to show at the top of the page
    stat_data = get_column_stats_from_df(df[column.name])

    vis_scripts = []
    visualizations = get_column_visualisations(
        column,
        df[[column.name]],
        vis_scripts,
        context={'style': 'max-width:{0}px; max-height:{1}px;'
                          'display:inline-block;'.format(
                               max_width,
                               max_height
                          )
        }
    )

    return stat_data, vis_scripts, visualizations


@user_passes_test(is_instructor)
def stat_column(request, pk):
    """
    Render the page with stats and visualizations for the given column
    The page includes the following visualizations:
      First row: quartile information (only for integer and double)
      V1. Box plot. Only for columns of type integer and double.
      V2. Histogram. For columns of type integer, double, string, boolean

    :param request: HTTP request
    :param pk: primary key of the column
    :return: Render the page
    """

    workflow = get_workflow(request)
    if not workflow:
        return redirect('home')

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return redirect('home')

    stat_data, vis_scripts, visualizations = \
        get_column_visualization_items(workflow, column)

    return render(request,
                  'table/stat_column.html',
                  {'column': column,
                   'stat_data': stat_data,
                   'vis_scripts': vis_scripts,
                   'visualizations': [v.html_content for v in visualizations]}
                  )


@user_passes_test(is_instructor)
def stat_column_JSON(request, pk):
    """
    Function to respond a JSON GET request to show the column statistics
    in a modal
    :param request: HTTP request
    :param pk: Column primary key
    :return: HTML rendering of the visualization
    """

    # To include in the JSON response
    data = dict()

    # Get the workflow to obtain row numbers
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Get column, must be in the workflow
    column = workflow.columns.filter(pk=pk).first()
    if not column or column.is_key:
        # Something went wrong, the column requested does not belong to the
        # workflow selected, or the column requested is a key column
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Request to see the statistics for a non-key column that belongs to the
    # selected workflow

    stat_data, __, visualizations = \
        get_column_visualization_items(workflow,
                                       column,
                                       max_height=250,
                                       max_width=468)

    # Create the right key/value pair in the result dictionary
    data['html_form'] = render_to_string(
        'table/includes/partial_column_stats_modal.html',
        context={'column': column,
                 'stat_data': stat_data,
                 'visualizations': [v.html_content for v in visualizations]},
        request=request
    )

    return JsonResponse(data)


@user_passes_test(is_instructor)
def stat_row(request):
    """
    Render the page with stats and visualizations for a row in the table.
    The request must include key and value to get the right row. In
    principle, there is a visualisation for each row.

    :param request: HTTP request
    :return: Render the page
    """

    return get_row_visualisations(request)


@user_passes_test(is_instructor)
def stat_row_view(request, pk):
    """
    Render the page with stats and visualizations for a row in the table and
    a view (subset of columns).
    The request must include key and value to get the right row. In
    principle, there is a visualisation for each row.

    :param request: HTTP request
    :param pk: View id to use
    :return: Render the page
    """

    return get_row_visualisations(request, pk)


@user_passes_test(is_instructor)
def stat_table(request):
    """
    Render the page with stats and visualizations for the whole table.

    :param request: HTTP request
    :return: Render the page
    """

    return get_view_visualisations(request)


@user_passes_test(is_instructor)
def stat_table_view(request, pk):
    """
    Render the page with stats and visualizations for a view.

    :param request: HTTP request
    :param pk: View id to use
    :return: Render the page
    """

    return get_view_visualisations(request, pk)
