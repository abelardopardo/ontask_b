# -*- coding: utf-8 -*-

"""Functions to support stats visualisation."""
from typing import Any, Dict, List, Optional, Tuple

from django.utils.translation import ugettext as _
from pandas import DataFrame

from ontask import models
from ontask.dataops.pandas import get_column_statistics, load_table
from ontask.dataops.sql.row_queries import get_row
from ontask.visualizations.plotly import PlotlyBoxPlot, PlotlyColumnHistogram

VISUALIZATION_WIDTH = 600
VISUALIZATION_HEIGHT = 400


def _get_df_and_columns(
    workflow: models.Workflow,
    pk: int,
) -> Optional[Tuple[DataFrame, List, models.View]]:
    """Get the DF and the columns to process.

    :param workflow: Workflow object
    :param pk: Optional id for a view
    :return: Tuple DataFrame, List of columns (None, None if error
    """
    # If a view is given, filter the columns
    view = None
    if pk:
        view = workflow.views.filter(pk=pk).first()
        if not view:
            # View not found. Redirect to workflow detail
            return None
        columns_to_view = view.columns.filter(is_key=False)

        df = load_table(
            workflow.get_data_frame_table_name(),
            [col.name for col in columns_to_view],
            view.formula)
    else:
        # No view given, fetch the entire data frame
        columns_to_view = workflow.columns.filter(is_key=False)
        df = load_table(
            workflow.get_data_frame_table_name(),
            [col.name for col in columns_to_view])

    return df, columns_to_view, view


def _get_column_visualisations(
    column: models.Column,
    col_data: List,
    vis_scripts: List,
    viz_id: Optional[str] = '',
    single_val: Optional[str] = None,
    context: Optional[Dict] = None,
) -> List[str]:
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
    :return: List of Javascript code
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


def get_column_visualization_items(
    workflow: models.Workflow,
    column: models.Column,
) -> Tuple[Dict, List, List[str]]:
    """Get the visualization items (scripts and HTML) for a column.

    :param workflow: Workflow being processed
    :param column: Column requested
    :return: Tuple stat_data with descriptive stats, visualization scripts and
    visualization HTML
    """
    # Get the dataframe
    df = load_table(workflow.get_data_frame_table_name(), [column.name])

    # Extract the data to show at the top of the page
    stat_data = get_column_statistics(df[column.name])

    visualizations = _get_column_visualisations(
        column,
        df[[column.name]],
        [],
        context={
            'style': 'width:100%; height:100%;' + 'display:inline-block;'},
    )

    return stat_data, [], visualizations


def get_table_visualization_items(
    workflow: models.Workflow,
    rowselect_key: Optional[str] = None,
    rowselect_val: Optional[Any] = None,
    pk: Optional[int] = None,
) -> Optional[Tuple[str, Dict]]:
    """Get a tuple with a template, and a dictionary to visualize a table.

    :param workflow: Workflow being processed
    :param rowselect_key: Optional key name to select a row
    :param rowselect_val: Optional value to select a row
    :param pk: Primary key of a view (could be none)
    :return:
    """
    # Get the data frame and the columns
    df_col_view = _get_df_and_columns(workflow, pk)
    if not df_col_view:
        return None
    df, columns_to_view, view = df_col_view

    if bool(rowselect_key):
        template = 'table/stat_row.html'
        row = get_row(
            workflow.get_data_frame_table_name(),
            rowselect_key,
            rowselect_val,
            column_names=[col.name for col in columns_to_view],
        )
    else:
        row = None
        template = 'table/stat_view.html'

    vis_scripts = []
    visualizations = []
    context = {
        'style': 'max-width:{0}px; max-height:{1}px; margin: auto;'.format(
            VISUALIZATION_WIDTH,
            VISUALIZATION_HEIGHT),
    }
    for idx, column in enumerate(columns_to_view):

        # Add the title and surrounding container
        visualizations.append(
            '<hr/><h4 class="text-center">' + column.name + '</h4>')
        # If all values are empty, no need to proceed
        if all(not col_data for col_data in df[column.name]):
            visualizations.append(
                '<p>' + _('No values in this column') + '</p>')
            continue

        if row and not row[column.name]:
            visualizations.append(
                '<p class="alert-warning">' + _('No value in this column')
                + '</p>',
            )

        column_viz = _get_column_visualisations(
            column,
            df[[column.name]],
            vis_scripts=vis_scripts,
            viz_id='column_{0}'.format(idx),
            single_val=row[column.name] if row else None,
            context=context)

        visualizations.extend([vis.html_content for vis in column_viz])

    return template, {
        'value': rowselect_val,
        'view': view,
        'vis_scripts': vis_scripts,
        'visualizations': visualizations}
