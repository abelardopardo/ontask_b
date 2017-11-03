# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
from django.conf import settings

from action.models import Condition
from dataops import formula_evaluation
from dataops.pandas_db import (
    create_table_name,
    create_upload_table_name,
    store_table,
    df_column_types_rename,
    load_table,
    get_table_data,
    is_matrix_in_db,
    get_table_queryset,
    pandas_datatype_names)
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
             If temporary = False, return None. All this infor is stored in
             the workflow
    """

    if settings.DEBUG:
        print('Storing table ', table_name)

    # get column names and types
    df_column_names = map(clean_column_name, list(data_frame.columns))
    df_column_types = df_column_types_rename(data_frame)

    # if the data frame is temporary, the procedure is much simpler
    if temporary:
        # Get the if the columns have unique values per row
        column_unique = are_unique_columns(data_frame)

        # Store the table in the DB
        store_table(data_frame, table_name)

        # Return a list with three list with information about the
        # data frame that will be needed in the next steps
        return [df_column_names, df_column_types, column_unique]

    # We are modifying an existing DF

    # Get the workflow and its columns
    workflow = Workflow.objects.get(id=pk)
    wf_columns = Column.objects.filter(workflow__id=pk)

    # Loop over the columns in the data frame and reconcile the column info
    # with the column objects attached to the WF
    has_new_columns = False
    for cname in df_column_names:
        # See if this is a new column
        wf_column = next((x for x in wf_columns if x.name == cname), None)
        if not wf_column:
            # This column is new
            has_new_columns = True

            # Create a valid name if needed
            clean_name = clean_column_name(cname)
            if clean_name != cname:
                # Rename the column in the df
                data_frame.rename(columns={cname, clean_name}, inplace=True)

            Column.objects.create(
                name=clean_name,
                workflow=workflow,
                data_type=pandas_datatype_names[
                    data_frame[clean_name].dtype.name],
                is_key=is_unique_column(data_frame[clean_name]))

    # Get now the new set of columns with names
    wf_column_names = Column.objects.filter(
        workflow__id=pk).values_list('name', flat=True)

    # Reorder the columns in the data frame
    data_frame = data_frame[list(wf_column_names)]

    # Store the table in the DB
    store_table(data_frame, table_name)

    if has_new_columns:
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


def detect_datetime_columns(data_frame):
    """
    Given a data frame traverse the columns and those that have type "string"
    try to see if it is of type datetime. If so, apply the translation.
    :param df:
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
