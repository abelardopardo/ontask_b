# -*- coding: utf-8 -*-

"""Functions to support stats visualisation."""
from typing import Dict, List, Optional, Tuple

from django.utils.translation import gettext as _
from pandas import DataFrame
import pandas as pd

from ontask import models
from ontask.dataops import pandas
from ontask.visualizations.plotly import PlotlyBoxPlot, PlotlyColumnHistogram

VISUALIZATION_WIDTH = 600
VISUALIZATION_HEIGHT = 400


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


def get_df_and_columns(
    workflow: models.Workflow,
    view: Optional[models.View],
) -> Optional[Tuple[DataFrame, List]]:
    """Get the DF and the columns to process.

    :param workflow: Workflow object
    :param view: Optional view (None if not  needed
    :return: Tuple DataFrame, List of columns.
    """
    if view:
        columns_to_view = view.columns.filter(is_key=False)
        df = pandas.load_table(
            workflow.get_data_frame_table_name(),
            [col.name for col in columns_to_view],
            view.formula)
    else:
        # No view given, fetch the entire data frame
        columns_to_view = workflow.columns.filter(is_key=False)
        df = pandas.load_table(
            workflow.get_data_frame_table_name(),
            [col.name for col in columns_to_view])

    return df, columns_to_view


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
    df = pandas.load_table(workflow.get_data_frame_table_name(), [column.name])

    # Extract the data to show at the top of the page
    stat_data = pandas.get_column_statistics(df[column.name])

    visualizations = _get_column_visualisations(
        column,
        df[[column.name]],
        [],
        context={
            'style': 'width:100%; height:100%;' + 'display:inline-block;'},
    )

    return stat_data, [], visualizations


def get_table_visualization_items(
    data_frame: pd.DataFrame,
    columns_to_view: List[models.Column],
    row: Optional,
) -> Tuple[List, List]:
    """Get the HTML snippets to visualize the given list of columns.

    :param data_frame: Data frame containing the data
    :param columns_to_view: List of columns to process
    :param row: Row of values to take as reference (optional)
    :return: Tuple with visualization scripts, and html snippets.
    """
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
        if all(not col_data for col_data in data_frame[column.name]):
            visualizations.append(
                '<p class="text-center">' +
                _('No values in this column') +
                '</p>')
            continue

        if row and not row[column.name]:
            visualizations.append(
                '<p class="alert-warning">' + _('No value in this column')
                + '</p>')

        column_viz = _get_column_visualisations(
            column,
            data_frame[[column.name]],
            vis_scripts=vis_scripts,
            viz_id='column_{0}'.format(idx),
            single_val=row[column.name] if row else None,
            context=context)

        visualizations.extend([vis.html_content for vis in column_viz])

    return vis_scripts, visualizations
