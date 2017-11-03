# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse

import logs.ops
from dataops import ops, pandas_db
from ontask import slugify
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .forms import SelectColumnUploadForm, SelectUniqueKeysForm


@user_passes_test(is_instructor)
def upload_s2(request):
    """
    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_unique_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    CREATES:

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    :param request: Web request
    :return: the dictionary upload_data in the session object
    """
    workflow = get_workflow(request)
    if not workflow:
        return reverse('workflow:index')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is no object, or it is an empty dict, it denotes a direct
        # jump to this step, get back to the dataops page
        return redirect('dataops:list')

    # Get the column names, types, and those that are unique from the data frame
    try:
        initial_columns = upload_data.get('initial_column_names')
        column_types = upload_data.get('column_types')
        src_is_unique_column = upload_data.get('src_is_unique_column')
    except KeyError:
        # The page has been invoked out of order
        return redirect(upload_data.get('step_1', 'dataops:list'))

    # Get or create the list with the renamed column names
    rename_column_names = upload_data.get('rename_column_names', None)
    if rename_column_names is None:
        rename_column_names = [slugify(x) for x in initial_columns]
        upload_data['rename_column_names'] = rename_column_names

    # Get or create list of booleans identifying columns to be uploaded
    columns_to_upload = upload_data.get('columns_to_upload', None)
    if columns_to_upload is None:
        columns_to_upload = [False] * len(initial_columns)
        upload_data['columns_to_upload'] = columns_to_upload

    # Create one of the context elements for the form. Pack the lists so that
    # they can be iterated in the template
    df_info = [list(i) for i in zip(column_types,
                                    src_is_unique_column,
                                    initial_columns,
                                    rename_column_names,
                                    columns_to_upload)]

    # Bind the form with the received data (remember unique columns)
    form = SelectColumnUploadForm(request.POST or None,
                                  unique_columns=src_is_unique_column)

    # Process the initial loading of the form and return
    if request.method != 'POST':
        # Update the dictionary with the session information
        request.session['upload_data'] = upload_data
        context = {'form': form,
                   'df_info': df_info,
                   'prev_step': reverse('dataops:csvupload1'),
                   'wid': workflow.id}

        if not ops.workflow_id_has_matrix(workflow.id):
            # It is an upload, not a merge, set the next step to finish
            context['next_name'] = 'Finish'
        return render(request, 'dataops/upload_s2.html', context)

    # At this point we are processing a POST request

    # If the form is not valid, re-load
    if not form.is_valid():
        context = {'form': form,
                   'wid': workflow.id,
                   'prev_step': reverse('dataops:csvupload1'),
                   'df_info': df_info}
        if not ops.workflow_id_has_matrix(workflow.id):
            # If it is an upload, not a merge, set next step to finish
            context['next_name'] = 'Finish'
        return render(request, 'dataops/upload_s2.html', context)

    # Form is valid

    # We need to modify df_info with the information received in the post
    for i in range(len(initial_columns)):
        new_name = form.cleaned_data['new_name_%s' % i]
        df_info[i][3] = new_name
        upload_data['rename_column_names'][i] = new_name
        upload = form.cleaned_data['upload_%s' % i]
        df_info[i][4] = upload
        upload_data['columns_to_upload'][i] = upload

    # Update the dictionary with the session information
    request.session['upload_data'] = upload_data

    # Load the existing DF or None if it doesn't exist
    existing_df = pandas_db.load_from_db(workflow.id)

    if existing_df is not None:
        # This is a merge operation, so move to Step 3
        return redirect('dataops:upload_s3')

    # This is an upload operation (not a merge) save the uploaded dataframe in
    # the DB and finish.

    # Get the uploaded data_frame
    try:
        data_frame = ops.load_upload_from_db(workflow.id)
    except Exception:
        return render(
            request,
            'error.html',
            {'message': 'Exception while retrieving the data frame'})

    # Update the data frame
    ops.perform_dataframe_upload_merge(workflow.id,
                                       existing_df,
                                       data_frame,
                                       upload_data)

    # Nuke the temporary table
    pandas_db.delete_upload_table(workflow.id)

    # Log the event
    col_info = workflow.get_column_info()
    logs.ops.put(request.user,
                 'workflow_data_upload',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'num_rows': workflow.nrows,
                  'num_cols': workflow.ncols,
                  'column_names': col_info[0],
                  'column_types': col_info[1],
                  'column_unique': col_info[2]})

    # Go back to show the detail of the data frame
    return redirect('dataops:list')


@user_passes_test(is_instructor)
def upload_s3(request):
    """

    Step 3: This is already a merge operation (not an upload)

    The columns to merge have been selected and renamed. The data frame to
    merge is called src.

    In this step the user selects the unique keys to perform the merge,
    the join method, and what to do with the columns that overlap (rename or
    override)

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_unique_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    CREATES:

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Unique column name selected in DST

    src_selected_key: Unique column name selected in SRC

    how_merge: How to merge. One of {left, right, outter, inner}

    how_dup_columns: How to handle column overlap

    autorename_column_names: Automatically modified column names

    :param request: Web request
    :return: the dictionary upload_data in the session object
    """
    # Get the workflow id we are processing
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect('dataops:list')

    # Get column names in dst_df
    dst_column_names = upload_data.get('dst_column_names', None)
    if not dst_column_names:
        dst_column_names = workflow.get_column_names()
        upload_data['dst_column_names'] = dst_column_names

    # Array of booleans saying which columns are unique in the dst DF.
    dst_is_unique_column = upload_data.get('dst_is_unique_column')
    if dst_is_unique_column is None:
        dst_is_unique_column = workflow.get_column_unique()
        upload_data['dst_is_unique_column'] = dst_is_unique_column

    # Array of unique col names in DST
    dst_unique_col_names = upload_data.get('dst_unique_col_names', None)
    if dst_unique_col_names is None:
        dst_unique_col_names = [v for x, v in enumerate(dst_column_names)
                                if dst_is_unique_column[x]]
        upload_data['dst_unique_col_names'] = dst_unique_col_names

    # Get the column names of the unique columns to upload in the DF to
    # merge (source)
    columns_to_upload = upload_data['columns_to_upload']
    src_column_names = upload_data['rename_column_names']
    src_is_unique_column = upload_data['src_is_unique_column']
    src_unique_col_names = [v for x, v in enumerate(src_column_names)
                            if src_is_unique_column[x] and columns_to_upload[x]]

    # Calculate the names of columns that overlap between the two data
    # frames. It is the intersection of the column names that are not key in
    # the existing data frame and those in the source DF that are selected,
    # renamed and not unique
    rename_column_names = upload_data['rename_column_names']
    are_overlap_cols = (
        # DST Column names that are not Keys
        (set(dst_column_names) - set(dst_is_unique_column)) &
        # SRC Column names that are renamed, selected and not unique
        set([x for x, y, z in zip(rename_column_names,
                                  columns_to_upload,
                                  src_is_unique_column)
             if y and not z])) != set([])

    # Bind the form with the received data (remember unique columns and
    # preselected keys.)'
    form = SelectUniqueKeysForm(
        request.POST or None,
        dst_keys=dst_unique_col_names,
        src_keys=src_unique_col_names,
        src_selected_key=upload_data.get('src_selected_key', None),
        dst_selected_key=upload_data.get('dst_selected_key', None),
        how_merge=upload_data.get('how_merge', None),
        how_dup_columns=upload_data.get('how_dup_columns', None),
        are_overlap_cols=are_overlap_cols,
    )

    # Process the initial loading of the form
    if request.method != 'POST':
        # Update the dictionary with the session information
        request.session['upload_data'] = upload_data
        return render(request, 'dataops/upload_s3.html',
                      {'form': form,
                       'prev_step': reverse('dataops:upload_s2'),
                       'wid': workflow.id})

    # We are processing a post request with the information given by the user

    # If the form is not valid, re-visit (nothing is checked so far...)
    if not form.is_valid():
        return render(request, 'dataops/upload_s3.html',
                      {'form': form,
                       'prev_step': reverse('dataops:upload_s3')})

    # Get the keys and merge method and store them in the session dict
    upload_data['dst_selected_key'] = form.cleaned_data['dst_key']
    upload_data['src_selected_key'] = form.cleaned_data['src_key']
    upload_data['how_merge'] = form.cleaned_data['how_merge']
    upload_data['how_dup_columns'] = \
        form.cleaned_data.get('how_dup_columns', None)

    # Check if there are overlapping columns and if rename was selected as
    # the method to deal with them. If so, create a list with the new
    # names (adding a numeric suffix)
    how_dup_columns = form.cleaned_data.get('how_dup_columns', None)
    autorename_column_names = []
    if are_overlap_cols and how_dup_columns == 'rename':
        # Columns must be renamed!
        # Initially the new list is identical to the previous one
        autorename_column_names = rename_column_names[:]
        for idx, col in enumerate(rename_column_names):
            # Skip the selected keys
            if col == upload_data['src_selected_key']:
                continue

            # If the column name is not in dst, no need to rename
            if col not in dst_column_names:
                continue

            # Column with a name that collides with one in the DST
            i = 0  # Suffix to rename
            while True:
                i += 1
                new_name = col + '_{0}'.format(i)
                if new_name not in rename_column_names and \
                        new_name not in dst_column_names:
                    break
            # Record the new created name in the resulting list
            autorename_column_names[idx] = new_name

    # Remember the autorename list for the next step
    upload_data['autorename_column_names'] = autorename_column_names

    # Update session object
    request.session['upload_data'] = upload_data

    return redirect('dataops:upload_s4')


@user_passes_test(is_instructor)
def upload_s4(request):
    """

    Step 4: Show the user the expected effect of the merge and perform it.

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_unique_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Unique column name selected in DST

    src_selected_key: Unique column name selected in SRC

    how_merge: How to merge. One of {left, right, outter, inner}

    how_dup_columns: How to handle column overlap

    autorename_column_names: Automatically modified column names

    override_columns_names: Names of dst columns that will be overridden in
    merge

    :param request: Web request
    :return:
    """
    # Get the workflow id we are processing
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect('dataops:list')

    # Create the information to include in the final report table
    dst_column_names = upload_data['dst_column_names']
    src_selected_key = upload_data['src_selected_key']
    # Triplets to show in the page (dst column, Boolean saying there is some
    # change, and the message on the src colummn
    autorename_column_names = upload_data['autorename_column_names']
    rename_column_names = upload_data['rename_column_names']
    info = []
    initial_column_names = upload_data['initial_column_names']

    # Create the strings to show in the table for each of the rows explaining
    # what is going to be the effect of the merge operation over them.
    override_columns_names = set([])
    for idx, (x, y, z) in enumerate(zip(initial_column_names,
                                        rename_column_names,
                                        upload_data['columns_to_upload'])):
        # There are several possible cases
        #
        # 1) The unique key. No message needed because it is displayed at
        #    the top of the rows
        # 2) The column has not been selected. Simply show (Ignored) in the
        #    right.
        # 3) Column is selected and is NEW
        # 4) Column is selected and was renamed by the user
        # 5) Column is selected and was automatically renamed by the tool
        #    when requesting to preserve the overlapping columns

        # CASE 1: If it is a key (compare the rename value in case user tried
        # to rename it.
        if y == src_selected_key:
            continue

        # CASE 2: Column not selected, thus simply print "Ignored")
        if not z:
            info.append(('', False, x + ' (Ignored)'))
            continue

        # Calculate the final name after the renaming
        final_name = x
        suffix = ''

        # Logic to figure out the final name after renaming
        if y != x:
            # If the corresponding name in rename_column_names is different,
            #  change
            final_name = y

            # To add to the column
            suffix = ', Renamed'

            # If autorename table exists, and the new name is different,
            # rename again
            if autorename_column_names and autorename_column_names[idx] != y:
                final_name = \
                    autorename_column_names[idx]
                suffix = ', Automatically renamed'
        else:
            # Check if there was autorename
            if autorename_column_names and \
                            autorename_column_names[idx] != x:
                final_name = \
                    autorename_column_names[idx]
                suffix = ', Automatically renamed'

        if final_name in dst_column_names:
            suffix = ' (Override' + suffix + ')'
            override_columns_names.add(final_name)
        else:
            suffix = ' (New' + suffix + ')'

        info.append((final_name + suffix, True, x))

    # Store the value in the request object.
    upload_data['override_columns_names'] = list(override_columns_names)

    if request.method != 'POST':
        request.session['upload_data'] = upload_data
        return render(request, 'dataops/upload_s4.html',
                      {'prev_step': reverse('dataops:upload_s3'),
                       'info': info,
                       'next_name': 'Finish'})

    # We are processing a POST request

    # Get the dataframes to merge
    try:
        dst_df = pandas_db.load_from_db(workflow.id)
        src_df = ops.load_upload_from_db(workflow.id)
    except Exception:
        return render(request,
                      'error.html',
                      {'message': 'Exception while loading data frame'})

    # Performing the merge
    status = ops.perform_dataframe_upload_merge(workflow.id,
                                                dst_df,
                                                src_df,
                                                upload_data)

    # Nuke the temporary table
    pandas_db.delete_upload_table(workflow.id)

    col_info = workflow.get_column_info()
    if status:
        logs.ops.put(request.user,
                     'workflow_data_failedmerge',
                     workflow,
                     {'id': workflow.id,
                      'name': workflow.name,
                      'num_rows': workflow.nrows,
                      'num_cols': workflow.ncols,
                      'column_names': col_info[0],
                      'column_types': col_info[1],
                      'column_unique': col_info[2],
                      'error_msg': status})

        messages.error(request, 'Merge operation failed.'),
        return render(request, 'dataops/upload_s4.html',
                      {'prev_step': reverse('dataops:upload_s3'),
                       'next_name': 'Finish'})

    # Log the event
    logs.ops.put(request.user,
                 'workflow_data_merge',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'num_rows': workflow.nrows,
                  'num_cols': workflow.ncols,
                  'column_names': col_info[0],
                  'column_types': col_info[1],
                  'column_unique': col_info[2]})

    # Remove the csvupload from the session object
    request.session.pop('upload_data', None)

    return redirect('dataops:list')
