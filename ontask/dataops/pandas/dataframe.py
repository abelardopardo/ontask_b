# -*- coding: utf-8 -*-

"""Operations to manipulate dataframes."""
from typing import Dict, List, Optional

from django.conf import settings
from django.utils.translation import gettext, ugettext_lazy as _
import numpy as np
import pandas as pd

from ontask.dataops import formula, pandas, sql


def _verify_dataframe_columns(
    workflow,
    data_frame: pd.DataFrame,
):
    """Verify that the df columns are compatible with those in the wflow.

    This function is crucial to make sure the information stored in the
    workflow and the one in the dataframe is consistent. It it assumed that
    the data frame given as parameter contains a superset of the columns
    already present in the workflow. The function traverses those columns in
    the data frame that are already included in the workflow and checks the
    following conditions:

    1) The value of is_key is preserved. If not, the offending column should
    have reached this stage with is_key equal to False

    2) The data types stored in the column.data_type field is consistent with
    that observed in the data frame.

       2.1) A column of type bool must be of type string in the DF but with
       values None, True, False.

       2.2) A column of type integer or double in the WF must be either integer
       or double in the Dataframe. If it is double, it will be updated at a
       later stage.

       2.3) If a column is not of type string or integer, and has a type change
       it is flagged as an error.

    3) If the WF column has categories, the values in the DF should be
    compatible.
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
        if col.is_key and not pandas.is_unique_column(data_frame[col.name]):
            raise Exception(gettext(
                'Column {0} looses its "key" property through this merge.'
                + ' Either remove this property from the column or '
                + 'remove the rows that cause this problem in the new '
                + 'dataset').format(col.name))

        # Get the pandas data type
        df_col_type = pandas.datatype_names.get(
            data_frame[col.name].dtype.name)

        # Condition 2: Review potential data type changes
        if col.data_type == 'boolean' and df_col_type == 'string':
            # 2.1: A WF boolean with must be DF string with True/False/None
            column_data_types = {
                type(row_value)
                for row_value in data_frame[col.name]
                # Remove the NoneType and Float
                if not isinstance(row_value, float) and row_value is not None
            }
            if len(column_data_types) != 1 or column_data_types.pop() != bool:
                raise Exception(gettext(
                    'New values in column {0} are not of type {1}',
                ).format(col.name, col.data_type))
        elif (
            col.data_type == 'integer' and df_col_type != 'integer'
            and df_col_type != 'double'
        ):
            # 2.2 WF Numeric column must be DF integer or double
            raise Exception(gettext(
                'New values in column {0} are not of type number',
            ).format(col.name))
        elif col.data_type != 'integer' and df_col_type != col.data_type:
            # 2.3 Any other type change is incorrect
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


def store_temporary_dataframe(
    data_frame: pd.DataFrame,
    workflow,
):
    """Store a temporary dataframe.

    :param data_frame: Data frame to store
    :param workflow: Data frame will belong to this workflow
    :return: List of three lists:
        - Data frame columns
        - Column types (OnTask)
        - List of booleans denoting if the column is unique
    """
    table_name = workflow.get_upload_table_name()

    # Get the if the columns have unique values per row
    column_unique = pandas.are_unique_columns(data_frame)

    # Store the table in the DB
    pandas.store_table(data_frame, table_name)

    # Get the column types
    df_column_types = sql.get_df_column_types(table_name)

    # Return a list with three list with information about the
    # data frame that will be needed in the next steps
    return [list(data_frame.columns), df_column_types, column_unique]


def store_dataframe(
    data_frame: pd.DataFrame,
    workflow,
):
    """Update or create a table in the DB with the data in the data frame.

    It also updates the corresponding column information

    :param data_frame: Data frame to dump to DB
    :param workflow: Corresponding workflow
    :return: Nothing. All this info is stored in the workflow
    """
    _verify_dataframe_columns(workflow, data_frame)

    # Store the data frame temporarily in the DB (use type-inference)
    df_columns, col_types, is_key = store_temporary_dataframe(
        data_frame,
        workflow)

    # Update the temporary DF in the DB to the official workflow table.
    store_workflow_table(
        workflow,
        {
            'initial_column_names': df_columns,
            'column_types': col_types,
            'keep_key_column': is_key})


def store_workflow_table(
    workflow,
    update_info: Optional[Dict] = None,
):
    """Make a temporary DB table the workflow table.

    It is assumed that there is a temporal table already in the database. The
    function performs the following steps:

    Step 1: Drop the columns that are not being uploaded

    Step 2: Rename the columns (if needed)

    Step 3: Create the workflow columns

    Step 4: Rename the table (temporary to final)

    Step 5: Update workflow fields and update

    :param workflow: Workflow object being manipulated.
    :param update_info: Dictionary with the following fields:
        - initial_column_names: list of column names detected in read phase.
        - rename_column_names: List of new names for the columns
        - column_types: List of types detected after storing in DB
        - keep_key_column: List of booleans to flag if key property is kept
        - columns_to_upload: List of booleans to flag column upload
        The first field is mandatory. The have default values if not provided.
    :return: Nothing. Anomalies are raised as Exceptions
    """
    # Check information on update_info and complete if needed
    if not update_info.get('initial_column_names'):
        raise _('Internal error while processing database.')
    if not update_info.get('rename_column_names'):
        update_info['rename_column_names'] = update_info[
            'initial_column_names']
    if not update_info.get('column_types'):
        raise _('Internal error while processing database.')
    if not update_info.get('keep_key_column'):
        raise _('Internal error while processing database.')
    if not update_info.get('columns_to_upload'):
        update_info['columns_to_upload'] = [True] * len(update_info[
            'initial_column_names'])

    db_table = workflow.get_upload_table_name()
    new_columns = []
    for old_n, new_n, data_type, is_key, upload in zip(
        update_info['initial_column_names'],
        update_info['rename_column_names'],
        update_info['column_types'],
        update_info['keep_key_column'],
        update_info['columns_to_upload'],
    ):
        # Detect if the column is new or already exists
        current_col = workflow.columns.filter(name=old_n).first()

        # Step 1: Check if column needs to be uploaded
        if not upload:
            # Column is dropped
            sql.df_drop_column(db_table, old_n)

            if current_col:
                # Dropping an existing column. Incorrect.
                raise _('Invalid column drop operation.')
            continue

        # Step 2: Check if the column must be renamed
        if old_n != new_n:
            # Rename column from old_n to new_n
            sql.db_rename_column(db_table, old_n, new_n)

            if current_col:
                rename_df_column(workflow, old_n, new_n)

        if current_col:
            if current_col.data_type != data_type:
                # If the column type in the DB is different from the one in the
                # object, update
                current_col.data_type = data_type
                current_col.save()
        else:
            # Step 3: Create the column
            new_columns.append((new_n, data_type, is_key))

    # Create the columns
    workflow.add_columns(new_columns)
    workflow.refresh_from_db()

    # Step 4: Rename the table (Drop the original one first
    if workflow.has_table():
        sql.delete_table(workflow.get_data_frame_table_name())
    sql.rename_table(db_table, workflow.get_data_frame_table_name())

    # Step 5: Update workflow fields and save
    workflow.nrows = sql.get_num_rows(workflow.get_data_frame_table_name())
    workflow.set_query_builder_ops()
    workflow.save(update_fields=['nrows', 'query_builder_ops'])


def get_table_row_by_index(
    workflow,
    filter_formula,
    idx: int,
):
    """Select the set of elements in the row with the given index.

    :param workflow: Workflow object storing the data
    :param filter_formula: Condition object to filter the data (or None)
    :param idx: Row number to get (first row is idx = 1)
    :return: A dictionary with the (column_name, value) data or None if the
     index is out of bounds
    """
    # Get the data
    df_data = sql.get_rows(
        workflow.get_data_frame_table_name(),
        column_names=workflow.get_column_names(),
        filter_formula=filter_formula)

    # If the data is not there, return None
    if idx > df_data.rowcount:
        return None

    return df_data.fetchall()[idx - 1]


def add_column_to_df(
    df: pd.DataFrame,
    column,
    initial_value=None,
) -> pd.DataFrame:
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


def rename_df_column(
    workflow,
    old_name: str,
    new_name: str,
):
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
        view.formula = formula.evaluation.rename_variable(
            view.formula,
            old_name,
            new_name)
        view.save(update_fields=['formula'])


def get_subframe(
    table_name: str,
    filter_formula,
    column_names: List[str],
) -> pd.DataFrame:
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
        sql.get_rows(
            table_name,
            column_names=column_names,
            filter_formula=filter_formula,
        ).fetchall(),
        columns=column_names,
        coerce_float=True)
