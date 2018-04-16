# -*- coding: utf-8 -*-
"""
Implementation of views providing visualisation and stats
"""
from __future__ import unicode_literals, print_function

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render

from dataops import pandas_db
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
        return redirect('workflow:index')

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
                      {'message': 'Unable to update table row'})

    # Get the dataframe
    df = pandas_db.load_from_db(workflow.id)

    # If a view is given, filter the columns.
    if view_id:
        try:
            view = View.objects.get(pk=view_id)
        except ObjectDoesNotExist:
            # View not found. Redirect to workflow detail
            return redirect('workflow:detail', workflow.id)
        columns_to_view = view.columns.all()
        column_names = [c.name for c in columns_to_view]
    else:
        columns_to_view = workflow.columns.all()
        column_names = None

    # Get the rows from the table
    row = pandas_db.execute_select_on_table(workflow.id,
                                            [update_key],
                                            [update_val],
                                            column_names)[0]

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
        visualizations.append(
            '<div style="display: inline-flex;">'
        )

        v = get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts = vis_scripts,
            id='column_{}'.format(idx),
            single_val=row[idx],
            context=context)

        visualizations.extend([x.html_content for x in v])
        visualizations.append('<hr/></div>')

    return render(request,
                  'table/stat_row.html',
                  {'value': update_val,
                   'vis_scripts': vis_scripts,
                   'visualizations': visualizations})



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
        return redirect('workflow:index')

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return redirect('workflow:index')

    # Get the dataframe
    df = pandas_db.load_from_db(workflow.id)

    # Extract the data to show at the top of the page
    stat_data = pandas_db.get_column_stats_from_df(df[column.name])

    vis_scripts = []
    visualizations = get_column_visualisations(column,
                                               df[[column.name]],
                                               vis_scripts)

    return render(request,
                  'table/stat_column.html',
                  {'column': column,
                   'stat_data': stat_data,
                   'vis_scripts': vis_scripts,
                   'visualizations': [v.html_content for v in visualizations]}
                  )


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