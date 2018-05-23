# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import numpy as np
import pandas as pd
from django.conf import settings

from action.models import Condition, Action
from dataops import formula_evaluation
from dataops.pandas_db import (
    create_table_name,
    create_upload_table_name,
    store_table,
    df_column_types_rename,
    load_table,
    get_table_data,
    is_table_in_db,
    get_table_queryset,
    pandas_datatype_names)
from table.models import View
from workflow.models import Workflow, Column


def is_unique_column(df_column):
    """

    :param df_column: Column of a pandas data frame
    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.dropna().unique()) == len(df_column)


def are_unique_columns(data_frame):
    """

    :param data_frame: Pandas data frame
    :return: Array of Booleans stating of a column has unique values
    """
    return [is_unique_column(data_frame[x]) for x in list(data_frame.columns)]


def load_upload_from_db(pk):
    return load_table(create_upload_table_name(pk))


def store_table_in_db(data_frame, pk, table_name, temporary=False):
    """
    Update or create a table in the DB with the data in the data frame. It
    also updates the corresponding column information

    :param data_frame: Data frame to dump to DB
    :param pk: Corresponding primary key of the workflow
    :param table_name: Table to use in the DB
    :param temporary: Boolean stating if the table is temporary,
           or it belongs to an existing workflow.
    :return: If temporary = True, then return a list with three lists:
             - column names
             - column types
             - column is unique
             If temporary = False, return None. All this info is stored in
             the workflow
    """

    if settings.DEBUG:
        print('Storing table ', table_name)

    # get column names
    df_column_names = list(data_frame.columns)

    # if the data frame is temporary, the procedure is much simpler
    if temporary:
        # Get the if the columns have unique values per row
        column_unique = are_unique_columns(data_frame)

        # Store the table in the DB
        store_table(data_frame, table_name)

        # Get the column types
        df_column_types = df_column_types_rename(table_name)

        # Return a list with three list with information about the
        # data frame that will be needed in the next steps
        return [df_column_names, df_column_types, column_unique]

    # We are modifying an existing DF

    # Get the workflow and its columns
    workflow = Workflow.objects.get(id=pk)
    wf_col_names = Column.objects.filter(
        workflow__id=pk
    ).values_list("name", flat=True)

    # Loop over the columns in the data frame and reconcile the column info
    # with the column objects attached to the WF
    for cname in df_column_names:
        # See if this is a new column
        if cname in wf_col_names:
            # If column already exists in wf_col_names, no need to do anything
            continue

        # Create the new column
        column = Column(
            name=cname,
            workflow=workflow,
            data_type=pandas_datatype_names[data_frame[cname].dtype.name],
            is_key=is_unique_column(data_frame[cname]),
            position=Column.objects.filter(workflow=workflow).count() + 1,
        )
        column.save()

    # Get now the new set of columns with names
    wf_columns = Column.objects.filter(
        workflow__id=pk)

    # Reorder the columns in the data frame
    data_frame = data_frame[[x.name for x in wf_columns]]

    # Store the table in the DB
    store_table(data_frame, table_name)

    # Review the column types because some "objects" are stored as booleans
    # TODO: Review this process to optimise
    column_types = df_column_types_rename(table_name)
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
    workflow.data_frame_table_name = table_name
    workflow.save()

    return None


def store_dataframe_in_db(data_frame, pk):
    """
    Given a dataframe and the primary key of a workflow, it dumps its content on
    a table that is rewritten every time.

    :param data_frame: Pandas data frame containing the data
    :param pk: The unique key for the workflow
    :return: Nothing. Side effect in the database
    """
    return store_table_in_db(data_frame, pk, create_table_name(pk))


def store_upload_dataframe_in_db(data_frame, pk):
    """
    Given a dataframe and the primary key of a workflow, it dumps its content on
    a table that is rewritten every time.

    :param data_frame: Pandas data frame containing the data
    :param pk: The unique key for the workflow
    :return: If temporary = True, then return a list with three lists:
             - column names
             - column types
             - column is unique
             If temporary = False, return None. All this infor is stored in
             the workflow
    """
    return store_table_in_db(data_frame,
                             pk,
                             create_upload_table_name(pk),
                             True)


def get_table_row_by_index(workflow, cond_filter, idx):
    """
    Select the set of elements in the row with the given index

    :param workflow: Workflow object storing the data
    :param cond_filter: Condition object to filter the data (or None)
    :param idx: Row number to get (first row is idx = 1)
    :return: A dictionary with the (column_name, value) data or None if the
     index is out of bounds
    """

    # Get the data
    data = get_table_data(workflow.id, cond_filter)

    # If the data is not there, return None
    if idx > len(data):
        return None

    return dict(zip(workflow.get_column_names(), data[idx - 1]))


def workflow_has_table(workflow_item):
    return is_table_in_db(create_table_name(workflow_item.id))


def workflow_id_has_table(workflow_id):
    return is_table_in_db(create_table_name(workflow_id))


def workflow_has_upload_table(workflow_item):
    return is_table_in_db(
        create_upload_table_name(workflow_item.id)
    )


def get_queryset_by_workflow(workflow_item):
    return get_table_queryset(create_table_name(workflow_item.id))


def get_queryset_by_workflow_id(workflow_id):
    return get_table_queryset(create_table_name(workflow_id))


def perform_overlap_update(dst_df, src_df, dst_key, src_key, how_merge):
    """
    :param dst_df: Left data frame with all the columns
    :param src_df: Right data frame with the overlapping columns
    :param dst_key: Left key column
    :param src_key: Right key column
    :param how_merge: Merge version: inner, outer, left or right
    :return: Returns the updated data frame depending on the type of merge
    variant requested.

    For this function the 'update' and 'append' functions in Pandas will be
    used.

    The 'update' function will be used for those rows for
    which there is a corresponding key in src_df. This means that the data in
    dst_df_tmp1 will only be updated if the value is not NaN.

    The 'append' function will be used for those rows in src_df that are not
    present in dst_df.

    There are four possible cases for this STEP depending on the type of
    merge (inner, outer, left, right). Here is the pseudocode used for each
    of these cases:

    - left: Simplest case because this is exactly how the function 'update'
    behaves. So, in this case dst_df_tmp1.update(src_df[OVERLAP]) is the
    result.

    - inner: First obtain the subset dst_df_tmp1 with intersection of
    dst_df_tmp1 and src_df keys (result in dst_df_tmp2) and then update
    dst_df_tmp2 with src_df[OVERLAP]

    - outer: First apply the update operation in the left case, that is
    dst_df_tmp1.update(src_df[OVERLAP], select from src_df[OVERLAP] the rows
    that are not part of dst_df_tmp1, and then append these to dst_df_tmp1 to
    create the result dst_df_tmp2

    - right: This is the most complex. It requires first to subset
    dst_df_tmp1 with the intersection of the two keys (src and dst). Then,
    dst_df_tmp1 is updated with the content of src_df[OVERLAP]. Finally,
    the rows only in the src_df need to be appended to the dataframe.

    """
    # If the src data frame has a single column (they key), there is no need
    # to do any operation
    if len(src_df.columns) <= 1:
        return dst_df

    dst_df_tmp1 = dst_df.set_index(dst_key)
    src_df_tmp1 = src_df.set_index(src_key)
    if how_merge == 'inner':
        # Subset of dst_df_tmp1 with the keys in both DFs
        result = dst_df_tmp1.loc[
            dst_df_tmp1.index.intersection(src_df_tmp1.index)
        ]
        # Update the subset with the values in the right
        result.update(src_df_tmp1)
    elif how_merge == 'outer':
        # Update
        result = dst_df_tmp1
        result.update(src_df_tmp1)
        # Append the missing rows
        tmp1 = src_df_tmp1.loc[src_df_tmp1.index.difference(dst_df_tmp1.index)]
        if not tmp1.empty:
            # Append only if the tmp1 data frame is not empty (otherwise it
            # looses the name of the index column
            result = result.append(tmp1)
    elif how_merge == 'left':
        result = dst_df_tmp1
        result.update(src_df_tmp1)
    else:
        # Right merge
        # Subset of dst_df_tmp1 with the keys in both DFs
        tmp1 = dst_df_tmp1.loc[
            dst_df_tmp1.index.intersection(src_df_tmp1.index)
        ]
        # Update with the right DF
        tmp1.update(src_df_tmp1)
        # Append the rows that are in right and not in left
        tmp2 = src_df_tmp1.loc[src_df_tmp1.index.difference(dst_df_tmp1.index)]
        if not tmp2.empty:
            # Append only if it is not empty
            result = tmp1.append(tmp2)

    # Return result
    return result.reset_index()


def perform_dataframe_upload_merge(pk, dst_df, src_df, merge_info):
    """
    It either stores a data frame in the db (dst_df is None), or combines
    the two data frames dst_df and src_df and stores its content.

    The combination of dst_df and src_df assumes:

    - dst_df has a set of columns (potentially empty) that do not overlap in
      name with the ones in src_df (dst_df[NO_OVERLAP_DST])

    - dst_df and src_df have a set of columns (potentially empty) that overlap
      in name (dst_df[OVERLAP] and src_df[OVERLAP] respectively)

    - src_df has a set of columns (potentially empty) that do not overlap in
      name with the ones in dst_df (src_df[NO_OVERLAP_SRC])

    The function combines dst_df and src_df following two main steps (in both
    steps, the number of rows processed are derived from the parameter
    merge_info['how_merge']).

    STEP A: A new data frame dst_df_tmp1 is created using the pandas "merge"
    operation between dst_df and src_df[NO_OVERLAP_SRC]. This increases the
    number of columns in dst_df_tmp1 with respect to dst_df by adding the new
    columns from src_df.

    The pseudocode for this step is:

    dst_df_tmp1 = pd.merge(dst_df,
                           src_df[NO_OVERLAP_SRC],
                           how=merge['how_merge'],
                           left_on=merge_info['dst_selected_key'],
                           right_on=merge_info['src_selected_key'])

    STEP B: The data frame dst_df_tmp1 is then updated with the values in
    src_df[OVERLAP].

    :param pk: Primary key of the Workflow containing the data frames
    :param dst_df: Destination dataframe (already stored in DB)
    :param src_df: Source dataframe, stored in temporary table
    :param merge_info: Dictionary with merge options
           - initial_column_names: List of initial column names in src data
             frame.
           - rename_column_names: Columns that need to be renamed in src data
             frame.
           - columns_to_uplooad: Columns to be considered for the update
           - src_selected_key: Key in the source data frame
           - dst_selected_key: key in the destination (existing) data frame
           - how_merge: How to merge: inner, outer, left or right
    :return:
    """

    # STEP 1 Rename the column names.
    src_df = src_df.rename(
        columns=dict(zip(merge_info['initial_column_names'],
                         merge_info['rename_column_names'])))

    # STEP 2 Drop the columns not selected
    columns_to_upload = merge_info['columns_to_upload']
    src_df.drop([n for x, n in enumerate(list(src_df.columns))
                 if not columns_to_upload[x]],
                axis=1, inplace=True)

    # If no dst_df is given, simply dump the frame in the DB
    if dst_df is None:
        store_dataframe_in_db(src_df, pk)
        return None

    # Get the keys
    src_key = merge_info['src_selected_key']
    dst_key = merge_info['dst_selected_key']

    # STEP 3 Perform the combination
    # Separate the columns in src that overlap from those that do not
    # overlap, but include the key column in both data frames.
    overlap_names = set(dst_df.columns).intersection(src_df.columns)
    src_no_overlap_names = set(src_df.columns).difference(overlap_names)
    src_df_overlap = src_df[list(overlap_names.union({src_key}))]
    src_df_no_overlap = src_df[list(src_no_overlap_names.union({src_key}))]

    # Step A. Perform the merge of non-overlapping columns
    new_df = dst_df
    if len(src_df_no_overlap.columns) > 1:
        try:
            new_df = pd.merge(new_df,
                              src_df_no_overlap,
                              how=merge_info['how_merge'],
                              left_on=dst_key,
                              right_on=src_key)
        except Exception as e:
            return 'Merge operation failed. Exception: ' + e.message

        # VERY special case: The key used for the merge in src_df can have an
        # identical column in dst_df, but it is not the one used for the
        # merge. For example: DST has columns C1(key), C2, C3, SRC has
        # columns C2(key) and C4. The merge is done matching C1 in DST with
        # C2 in SRC, but this will produce two columns C2_x and C2_y. In this
        # case we drop C2_y because C2_x has been properly updated with the
        # values from C2_y in the previous step (Step A).
        if src_key != dst_key and src_key in dst_df.columns:
            # Drop column_y
            new_df.drop([src_key + '_y'], axis=1, inplace=True)
            # Rename column_x
            new_df = new_df.rename(columns={src_key + '_x': src_key})

    # Step B. Perform the update with the overlapping columns
    new_df = perform_overlap_update(new_df,
                                    src_df_overlap,
                                    dst_key,
                                    src_key,
                                    merge_info['how_merge'])

    # If the merge produced a data frame with no rows, flag it as an error to
    # prevent loosing data when there is a mistake in the key column
    if new_df.shape[0] == 0:
        return 'Merge operation produced a result with no rows'

    # For each column check that the new column is consistent with data_type,
    # and allowed values, and recheck its unique key status
    for col in Workflow.objects.get(pk=pk).columns.all():
        # New values in this column should be compatible with the current
        # column properties.
        # Condition 1: Data type is correct (there is an exception for columns
        # of type "object" in the data frame and "boolean" in the column as the
        # new resulting column may have a mix of booleans and floats.
        df_col_type = pandas_datatype_names[new_df[col.name].dtype.name]
        if col.data_type == 'boolean' and df_col_type == 'string':
            column_data_types = set([type(x) for x in new_df[col.name]])
            # Remove the NaN type
            column_data_types.remove(float)
            if len(column_data_types) != 1 or column_data_types.pop() != bool:
                return 'New values in column {0} are not of type {1}'.format(
                    col.name,
                    col.data_type
                )
        elif col.data_type == 'integer' and df_col_type != 'integer' and \
                df_col_type != 'double':
            # Numeric column results in a non-numeric column
            return 'New values in column {0} are not of type number'.format(
                col.name
            )
        elif col.data_type != 'integer' and df_col_type != col.data_type:
            # Any other type change
            return 'New values in column {0} are not of type {1}'.format(
                col.name,
                col.data_type
            )

        # Condition 2: If there are categories, the new values should be
        # compatible with them.
        if col.categories and not all([x in col.categories
                                       for x in new_df[col.name]]):
            return \
                'New values in column {0} are not in categories {1}'.format(
                    col.name,
                    ', '.join(col.categories)
                )

        # Condition 3:
        is_key_now = is_unique_column(new_df[col.name])
        if col.is_key and not is_key_now:
            return \
                'Column {0} is no longer a key column.'.format(col.name)

        col.is_key = is_key_now
        col.save()

    # Store the result back in the DB
    store_dataframe_in_db(new_df, pk)

    # Recompute all the values of the conditions in each of the actions
    for action in Workflow.objects.get(pk=pk).actions.all():
        action.update_n_rows_selected()

    # Operation was correct, no need to flag anything
    return None


def data_frame_add_column(df, column, initial_value):
    """

    :param df: Data frame to modify
    :param column: Column object to add
    :param initial_value: initial value in the column
    :return: new data frame with the additional column
    """

    # How to add a new column with a specific data type in DataFrame
    # a = np.empty((10,), dtype=[('column_name', np.float64)])
    # b = np.empty((10,), dtype=[('nnn', np.float64)] (ARRAY)
    # pd.concat([df, pd.DataFrame(b)], axis=1)

    column_type = column.data_type
    if initial_value is None:
        # Choose the right numpy type
        if column_type == 'string':
            initial_value = ''
        elif column_type == 'integer':
            initial_value = np.nan
        elif column_type == 'double':
            initial_value = np.nan
        elif column_type == 'boolean':
            initial_value = np.nan
        elif column_type == 'datetime':
            initial_value = pd.NaT
        else:
            raise ValueError('Type ' + column_type + ' not found.')

    # Create the empty column
    df[column.name] = initial_value

    return df


def rename_df_column(df, workflow, old_name, new_name):
    """
    Function to change the name of a column in the dataframe.

    :param df: dataframe
    :param workflow: workflow object that is handling the data frame
    :param old_name: old column name
    :param new_name: new column name
    :return: Workflow object updated
    """

    # Rename the appearances of the variable in all conditions/filters
    conditions = Condition.objects.filter(action__workflow=workflow)
    for cond in conditions:
        cond.formula = formula_evaluation.rename_variable(
            cond.formula, old_name, new_name)
        cond.save()

    # Rename the appearances of the variable in all actions
    for action_item in Action.objects.filter(workflow=workflow):
        action_item.rename_variable(old_name, new_name)

    # Rename the appearances of the variable in the formulas in the views
    for view in View.objects.filter(workflow=workflow):
        view.formula = formula_evaluation.rename_variable(
            view.formula,
            old_name,
            new_name
        )
        view.save()

    return df.rename(columns={old_name: new_name})


def detect_datetime_columns(data_frame):
    """
    Given a data frame traverse the columns and those that have type "string"
    try to see if it is of type datetime. If so, apply the translation.
    :param data_frame: Pandas dataframe to detect datetime columns
    :return:
    """
    # Strip white space from all string columns and try to convert to
    # datetime just in case
    for x in list(data_frame.columns):
        if data_frame[x].dtype.name == 'object':
            # Column is a string!
            data_frame[x] = data_frame[x].str.strip()

            # Try the datetime conversion
            try:
                series = pd.to_datetime(data_frame[x],
                                        infer_datetime_format=True)
                # Datetime conversion worked! Update the data_frame
                data_frame[x] = series
            except ValueError:
                pass
    return data_frame
