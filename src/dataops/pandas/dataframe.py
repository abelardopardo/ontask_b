# -*- coding: utf-8 -*-

"""Operations to manipulate dataframes."""

from builtins import zip

import numpy as np
import pandas as pd
from django.conf import settings
from django.utils.translation import gettext, ugettext_lazy as _

from dataops.formula import evaluation
from dataops.pandas.columns import are_unique_columns, is_unique_column
from dataops.pandas.datatypes import pandas_datatype_names
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


def _realign_column_info(workflow, data_frame):
    """Realign the column information between the data frame and the workflow.

    This function is crucial to make sure the information stored in the
    workflow and the one in the dataframe is consistent. It it assumed that
    the data frame given as parameter contains a superset of the columns
    already present in the workflow. This means:

    1) The Value of "is_key" needs to be updated.

    2) The data types stored in the column.data_type field is consistent with
    that observed in the data frame.

    3) If there are extra columns in the data_frame, they are created with
    the correct data types (and the information in the workflow object
    updated from the db)
    """
    df_column_names = list(data_frame.columns)
    wf_column_names = [col.name for col in workflow.columns.all()]

    if settings.DEBUG:
        # There should not be any columns in the workflow that are not in the
        # DF
        assert not (set(wf_column_names) - set(df_column_names))

    # Loop over the columns in the Workflow to refresh the is_key value. There
    # may be values that have been added to the column, so this field needs to
    # be reassessed
    for col in workflow.columns.all():
        # Condition 1: If the column is marked as a key column, it should
        # maintain this property
        if col.is_key and not is_unique_column(data_frame[col.name]):
            raise Exception(gettext(
                'Column {0} looses its "key" property through this merge.'
                + ' Either remove this property from the column or '
                + 'remove the rows that cause this problem in the new '
                + 'dataset').format(col.name))

        # Get the pandas data type
        df_col_type = pandas_datatype_names.get(
            data_frame[col.name].dtype.name)

        # Condition 2: Review potential data type changes
        if col.data_type == 'boolean' and df_col_type == 'string':
            column_data_types = {
                type(row_value)
                for row_value in data_frame[col.name]
                # Remove the NoneType and Float
                if type(row_value) != float and type(row_value) != type(None)
            }
            if len(column_data_types) != 1 or column_data_types.pop() != bool:
                raise Exception(gettext(
                    'New values in column {0} are not of type {1}',
                ).format(col.name, col.data_type))
        elif (
            col.data_type == 'integer' and df_col_type != 'integer'
            and df_col_type != 'double'
        ):
            # Numeric column results in a non-numeric column
            raise Exception(gettext(
                'New values in column {0} are not of type number',
            ).format(col.name))
        elif col.data_type != 'integer' and df_col_type != col.data_type:
            # Any other type change
            raise Exception(gettext(
                'New values in column {0} are not of type {1}',
            ).format(col.name, col.data_type))

        # Condition 3: If there are categories, the new values should be
        # compatible with them.
        if col.categories and not all(
            row_val in col.categories for row_val in data_frame[col.name]
            if row_val and not pd.isnull(row_val)
        ):
            raise Exception(gettext(
                'New values in column {0} are not in categories {1}',
            ).format(col.name, ', '.join(col.categories)))

        # Remove this column name from wf_col_names
        df_column_names.remove(col.name)

    # Loop over the remaining columns in the data frame and create them in the
    # workflow
    data_types = []
    is_unique = []
    for col_name in df_column_names:
        # Detect columns of type "object" in pandas that contain only bools and
        # True/False and marke them as
        if data_frame[col_name].dtype.name == 'object':
            column_data_types = {
                type(row_value)
                for row_value in data_frame[col_name]
                # Remove the NoneType and Float
                if type(row_value) != float and type(row_value) != type(None)
            }
            if len(column_data_types) == 1 and column_data_types.pop() == bool:
                data_types.append('bool')
            else:
                data_types.append(data_frame[col_name].dtype.name)
        else:
            data_types.append(data_frame[col_name].dtype.name)

        # Calculate the is_unique value
        is_unique.append(is_unique_column(data_frame[col_name]))

    # Create the new required columns
    workflow.add_new_columns(df_column_names, data_types, is_unique)


def store_dataframe(data_frame, workflow, temporary=False):
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
        print('Storing dataframe ', workflow.get_data_frame_table_name())

    _realign_column_info(workflow, data_frame)

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
        column_names=workflow.get_column_names(),
        filter_formula=filter_formula)

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
            column_names=column_names,
            filter_formula=filter_formula,
        ).fetchall(),
        columns=column_names,
        coerce_float=True)
