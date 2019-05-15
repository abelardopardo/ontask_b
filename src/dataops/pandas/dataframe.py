# -*- coding: utf-8 -*-

"""Operations to manipulate dataframes."""

from builtins import zip

import numpy as np
import pandas as pd
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from dataops.formula import evaluation
from dataops.pandas.datatypes import pandas_datatype_names
from dataops.pandas.columns import are_unique_columns, is_unique_column
from dataops.pandas.db import store_table
from dataops.sql.column_queries import get_df_column_types
from dataops.sql.row_queries import get_rows


def _store_temporary_dataframe(data_frame, workflow):
    """Store a temporary dataframe."""
    table_name = workflow.get_data_frame_upload_table_name()

    if settings.DEBUG:
        print('Storing table ', table_name)

    # Get the if the columns have unique values per row
    column_unique = are_unique_columns(data_frame)

    # Store the table in the DB
    store_table(data_frame, table_name)

    # Get the column types
    df_column_types = get_df_column_types(table_name)

    # Return a list with three list with information about the
    # data frame that will be needed in the next steps
    return [df_column_types, column_unique]


def _update_key_and_position(workflow, data_frame, wf_cols, reset_keys):
    """Update the is_key and position of the columns."""
    # Loop over the columns in the Workflow to refresh the is_key value. There
    # may be values that have been added to the column, so this field needs to
    # be reassessed
    df_column_names = list(data_frame.columns)
    for col in wf_cols:
        if reset_keys:
            new_val = is_unique_column(data_frame[col.name])
            if col.is_key and not new_val:
                # Only set the is_key value if the column states that it is a
                # key column, but the values say no. Othe other way around
                # is_key is false in the column will be ignored as it may have
                # been set by the user
                col.is_key = new_val
                col.save()

        # Remove this column name from wf_col_names, no further processing is
        # needed.
        df_column_names.remove(col.name)

    # Loop over the remaining columns in the data frame and create the new
    # column objects in the workflow
    workflow.add_new_columns(
        df_column_names,
        [data_frame[col].dtype.name for col in df_column_names],
        [is_unique_column(data_frame[col]) for col in df_column_names]
    )


def store_dataframe(data_frame, workflow, temporary=False, reset_keys=True):
    """Update or create a table in the DB with the data in the data frame.

    It also updates the corresponding column information

    :param data_frame: Data frame to dump to DB

    :param workflow: Corresponding workflow

    :param temporary: Boolean stating if the table is temporary,
           or it belongs to an existing workflow.

    :param reset_keys: Reset the value of the field is_key computing it from
           scratch

    :return: If temporary = True, then return a list with three lists:
             - column names
             - column types
             - column is unique
             If temporary = False, return None. All this info is stored in
             the workflow
    """
    # if the data frame is temporary, the procedure is much simpler
    if temporary:
        return [list(data_frame.columns)] + _store_temporary_dataframe(
            data_frame, workflow)

    # We are modifying an existing DF
    if settings.DEBUG:
        print('Storing table ', workflow.get_data_frame_table_name())

    _update_key_and_position(
        workflow,
        data_frame,
        workflow.columns.all(),
        reset_keys)

    # Refresh the workflow object and its set of columns
    workflow.refresh_from_db()
    wf_columns = workflow.columns.all()

    # Reorder the columns in the data frame
    data_frame = data_frame[[column.name for column in wf_columns]]

    # Store the table in the DB
    store_table(
        data_frame,
        workflow.get_data_frame_table_name(),
        dtype={col.name: col.data_type for col in wf_columns})

    # Review the column types because some "objects" are stored as booleans
    column_types = get_df_column_types(workflow.get_data_frame_table_name())
    for ctype, col in zip(column_types, wf_columns):
        if col.data_type != ctype:
            # If the column type in the DB is different from the one in the
            # object, update
            col.data_type = ctype
            col.save()

    # Update workflow fields and save
    workflow.nrows = data_frame.shape[0]
    workflow.ncols = data_frame.shape[1]
    workflow.set_query_builder_ops()
    workflow.save()

    return None


def get_table_row_by_index(workflow, filter_formula, idx):
    """Select the set of elements in the row with the given index.

    :param workflow: Workflow object storing the data

    :param filter_formula: Condition object to filter the data (or None)

    :param idx: Row number to get (first row is idx = 1)

    :return: A dictionary with the (column_name, value) data or None if the
     index is out of bounds
    """
    # Get the data
    df_data = get_rows(
        workflow.get_data_frame_table_name(),
        workflow.get_column_names(),
        filter_formula)

    # If the data is not there, return None
    if idx > df_data.rowcount:
        return None

    return df_data.fetchall()[idx - 1]


def add_column_to_df(df, column, initial_value=None):
    """Add a column to the data frame.

    Function that add a new column to the data frame with the structure to
    match the given column. If the initial value is not give, it is decided
    based on the data type stored in the column object.

    :param df: Data frame to modify

    :param column: Column object to add

    :param initial_value: initial value in the column

    :return: new data frame with the additional column
    """
    # Should we use pd.Series instead: pd.Series(dtype=np.int64)
    column_type = column.data_type
    if initial_value is None:
        # Choose the right numpy type
        if column_type == 'string':
            initial_value = None
        elif column_type == 'integer' or column_type == 'double':
            initial_value = np.nan
        elif column_type == 'boolean':
            initial_value = np.nan
        elif column_type == 'datetime':
            initial_value = pd.NaT
        else:
            raise ValueError(_('Type {0} not found').format(column_type))

    # Create the empty column
    df[column.name] = initial_value

    return df


def rename_df_column(workflow, old_name, new_name):
    """Change the name of a column in the dataframe.

    :param workflow: workflow object that is handling the data frame

    :param old_name: old column name

    :param new_name: new column name

    :return: Workflow object updated
    """
    # Rename the appearances of the variable in all actions
    for action_item in workflow.actions.prefetch_related('conditions').all():
        action_item.rename_variable(old_name, new_name)

    # Rename the appearances of the variable in the formulas in the views
    for view in workflow.views.all():
        view.formula = evaluation.rename_variable(
            view.formula,
            old_name,
            new_name)
        view.save()


def get_subframe(table_name, filter_formula, column_names) -> pd.DataFrame:
    """Load the subframe using the filter and column names.

    Execute a select query to extract a subset of the dataframe and turn the
     resulting query set into a data frame.

    :param table_name: Table

    :param filter_formula: Formula to filter the data (or None)

    :param column_names: [list of column names], QuerySet with the data rows

    :return: DataFrame
    """
    # Create the DataFrame and set the column names
    return pd.DataFrame.from_records(
        get_rows(
            table_name,
            column_names,
            filter_formula,
        ).fetchall(),
        columns=column_names,
        coerce_float=True)
