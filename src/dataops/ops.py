# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import numpy as np
import pandas as pd
from django.conf import settings

from action.models import Condition
from dataops import formula_evaluation

from dataops.pandas_db import (
    create_table_name,
    create_upload_table_name,
    delete_upload_table,
    store_table,
    df_column_types_rename,
    load_table,
    get_table_data,
    is_matrix_in_db,
    get_table_queryset)
from workflow.models import Workflow, Column


def is_unique_column(df_column):
    """

    :param df_column: Column of a pandas data frame
    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.unique()) == len(df_column)


def clean_column_name(val):
    """
    Function to transform column names and remove characters that are
    problematic with pandas <-> SQL (such as parenthesis)
    :param val:
    :return: New val
    """

    newval = val.replace('(', '[')
    return newval.replace(')', ']')


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
    also updates the fields column_names, column_types and column_unique

    :param data_frame: Data frame to dump to DB
    :param pk: Corresponding primary key of the workflow
    :param table_name: Table to use in the DB
    :param temporary: Boolean stating if the table is temporary,
           or it belongs to an existing workflow.
    :return: If temporary = True, then return a list with three lists:
             - column names
             - column types
             - column is unique
             If temporary = False, return None. All this infor is stored in
             the workflow
    """

    if settings.DEBUG:
        print('Storing table ', table_name)

    # Get the workflow and the columns assigned to it
    workflow = Workflow.objects.get(pk=pk)
    columns = Column.objects.filter(workflow__id=pk)

    # Manage the connection between columns in the DB and in the DF
    if not columns:
        # If there are no columns, automatically detect the unique ones
        column_names = map(clean_column_name, list(data_frame.columns))
        column_unique = are_unique_columns(data_frame)

        # Reorder the columns so that unique keys are at the top
        new_col_order = [(a, b)
                         for b, a in sorted(zip(column_unique, column_names),
                                            key=lambda x: (-x[0], x[1]))]

        # Get the new column names cleaned and ordered
        column_names = [x for x, _ in new_col_order]
        column_unique = [y for _, y in new_col_order]
    else:
        columns = workflow.columns.all()
        column_names = [x.name for x in columns]
        column_unique = [x.is_key for x in columns]

    # Reorder the columns in the data frame
    data_frame = data_frame[column_names]

    # Store the table in the DB
    store_table(data_frame, table_name)

    # Get the column data types
    column_types = df_column_types_rename(data_frame)

    # Distinguish between a matrix that is about to be uploaded/merged and
    # one that is already attached to a workflow.
    if temporary:
        # Return a list with three list with information about the
        # data frame that will be needed in the next steps
        return [column_names, column_types, column_unique]

    # At this point, we are storing the regular data frame (not a temporary
    # upload one)

    # Update workflow fields and save
    workflow.nrows = data_frame.shape[0]
    workflow.ncols = data_frame.shape[1]
    workflow.set_query_builder_ops()
    workflow.data_frame_table_name = table_name
    workflow.save()

    # Loop over the columns in the data frame and make sure the info is
    # consistent with the DB column objects
    for idx, cname in enumerate(list(data_frame.columns)):
        # Get the column object with the name, if it exists
        cobject = next((x for x in columns if x.name == cname), None)

        if cobject:
            # Column exists, so update its content
            cobject.data_type = column_types[idx]
            cobject.is_key = column_unique[idx]
            cobject.save()
        else:
            # Column does not exist, so create a new one
            Column.objects.create(
                name=column_names[idx],
                workflow=workflow,
                data_type=column_types[idx],
                is_key=column_unique[idx])

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


def workflow_has_matrix(workflow_item):
    return is_matrix_in_db(create_table_name(workflow_item.id))


def workflow_id_has_matrix(workflow_id):
    return is_matrix_in_db(create_table_name(workflow_id))


def get_queryset_by_workflow(workflow_item):
    return get_table_queryset(create_table_name(workflow_item.id))


def get_queryset_by_workflow_id(workflow_id):
    return get_table_queryset(create_table_name(workflow_id))


def workflow_table_info(workflow):
    """

    :param workflow: Workflow object from which to return the column info
    :return: dict with num_rows, num_columns and table dict with column names
    """
    # result to return
    table_info = None

    # Check if the workflow has a table
    if workflow_id_has_matrix(workflow.id):

        # start populating the result with Rows and columns
        table_info = {'num_rows': workflow.nrows, 'num_cols': workflow.ncols}

        # Columns are packed in tuples to be processed by template loop
        table_info['table'] = [
            {'id': col.id,
             'column_name': col.name,
             'column_type': col.data_type,
             'is_key': col.is_key}
            for col in workflow.columns.all()
        ]

    return table_info


def perform_dataframe_upload_merge(pk, dst_df, src_df, merge_info):
    """
    It either stores a data frame in the db (dst_df is None), or merges
    the two data frames dst_df and src_df and stores its content.

    :param pk: Primary key of the Workflow containing the data frames
    :param dst_df: Destination dataframe (already stored in DB)
    :param src_df: Source dataframe, stored in temporary table
    :param merge_info: Dictionary with merge options
    :return:
    """

    # STEP 1 Rename the column names.
    src_df = src_df.rename(
        columns=dict(zip(merge_info['initial_column_names'],
                         merge_info.get('autorename_column_names', None) or
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

    # Step 3. Drop the columns that are going to be overriden.
    dst_df.drop(merge_info['override_columns_names'],
                inplace=True,
                axis=1)

    # Step 4. Perform the merge
    try:
        new_df = pd.merge(dst_df,
                          src_df,
                          how=merge_info['how_merge'],
                          left_on=merge_info['dst_selected_key'],
                          right_on=merge_info['src_selected_key'])
    except Exception, e:
        return 'Merge operation failed. Exception: ' + e.message

    # Bring the data frame back to the database
    store_dataframe_in_db(new_df, pk)

    # Nuke the temporary table
    delete_upload_table(pk)

    return None  # Error message?


def data_frame_add_empty_column(df, column_name, column_type, initial_value):
    """

    :param df: Data frame to modify
    :param column_name: Name of the column to add
    :param column_type: type of the column to add
    :param initial_value: initial value in the column
    :return: new data frame with the additional column
    """

    # How to add a new column with a specific data type in DataFrame
    # a = np.empty((10,), dtype=[('column_name', np.float64)])
    # b = np.empty((10,), dtype=[('nnn', np.float64)] (ARRAY)
    # pd.concat([df, pd.DataFrame(b)], axis=1)

    if not initial_value:
        # Choose the right numpy type
        if column_type == 'string':
            initial_value = ''
        elif column_type == 'integer':
            initial_value = 0
        elif column_type == 'double':
            initial_value = 0.0
        elif column_type == 'boolean':
            initial_value = False
        elif column_type == 'datetime':
            initial_value = pd.NaT
        else:
            raise ValueError('Type ' + column_type + ' not found.')

    # Create the empty column
    df[column_name] = initial_value

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

    return df.rename(columns={old_name: new_name})
