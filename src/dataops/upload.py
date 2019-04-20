# -*- coding: utf-8 -*-


from builtins import range
from builtins import zip

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from dataops import ops, pandas_db
from logs.models import Log
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .forms import SelectColumnUploadForm, SelectKeysForm


@user_passes_test(is_instructor)
def upload_s2(request):
    """
    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    CREATES:

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    keep_key_column: Boolean list with those key columns that need to be kept.

    :param request: Web request
    :return: the dictionary upload_data in the session object
    """
    workflow = get_workflow(request, prefetch_related='columns')
    if not workflow:
        return redirect('home')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is no object, or it is an empty dict, it denotes a direct
        # jump to this step, get back to the dataops page
        return redirect('dataops:uploadmerge')

    # Get the column names, types, and those that are unique from the data frame
    try:
        initial_columns = upload_data.get('initial_column_names')
        column_types = upload_data.get('column_types')
        src_is_key_column = upload_data.get('src_is_key_column')
    except KeyError:
        # The page has been invoked out of order
        return redirect(upload_data.get('step_1',
                                        reverse('dataops:uploadmerge')))

    # Get or create the list with the renamed column names
    rename_column_names = upload_data.get('rename_column_names', None)
    if rename_column_names is None:
        rename_column_names = initial_columns[:]
        upload_data['rename_column_names'] = rename_column_names

    # Get or create list of booleans identifying columns to be uploaded
    columns_to_upload = upload_data.get('columns_to_upload', None)
    if columns_to_upload is None:
        columns_to_upload = [True] * len(initial_columns)
        upload_data['columns_to_upload'] = columns_to_upload

    # Get or create list of booleans identifying key columns to be kept
    keep_key_column = upload_data.get('keep_key_column', None)
    if keep_key_column is None:
        keep_key_column = upload_data['src_is_key_column'][:]
        upload_data['keep_key_column'] = keep_key_column

    # Bind the form with the received data (remember unique columns)
    form = SelectColumnUploadForm(
        request.POST or None,
        column_names=rename_column_names,
        columns_to_upload=columns_to_upload,
        is_key=src_is_key_column,
        keep_key=keep_key_column
    )

    # Get a hold of the fields to create a list to be processed in the page
    load_fields = [f for f in form if f.name.startswith('upload_')]
    newname_fields = [f for f in form if f.name.startswith('new_name_')]
    src_key_fields = [
        form['make_key_%s' % idx] if src_is_key_column[idx] else None
        for idx in range(len(src_is_key_column))
    ]

    # Create one of the context elements for the form. Pack the lists so that
    # they can be iterated in the template
    df_info = [list(i) for i in zip(load_fields,
                                    initial_columns,
                                    newname_fields,
                                    column_types,
                                    src_key_fields)]

    # Process the initial loading of the form and return
    if request.method == 'GET' or not form.is_valid():
        # Update the dictionary with the session information
        request.session['upload_data'] = upload_data
        context = {'form': form,
                   'wid': workflow.id,
                   'prev_step': upload_data['step_1'],
                   'valuerange': range(5) if workflow.has_table() else range(3),
                   'df_info': df_info}

        if not workflow.has_table():
            # It is an upload, not a merge, set the next step to finish
            context['next_name'] = _('Finish')
        return render(request, 'dataops/upload_s2.html', context)

    # At this point we are processing a valid POST request

    # We need to modify upload_data with the information received in the post
    for i in range(len(initial_columns)):
        new_name = form.cleaned_data['new_name_%s' % i]
        upload_data['rename_column_names'][i] = new_name
        upload = form.cleaned_data['upload_%s' % i]
        upload_data['columns_to_upload'][i] = upload

        if src_is_key_column[i]:
            # If the column is key, check if the user wants to keep it
            keep_key_column[i] = form.cleaned_data['make_key_%s' % i]

    # Update the dictionary with the session information
    request.session['upload_data'] = upload_data

    # Load the existing DF or None if it doesn't exist
    existing_df = pandas_db.load_from_db(workflow.get_data_frame_table_name())

    if existing_df is not None:
        # This is a merge operation, so move to Step 3
        return redirect('dataops:upload_s3')

    # This is an upload operation (not a merge) save the uploaded dataframe in
    # the DB and finish.

    # Get the uploaded data_frame
    try:
        data_frame = pandas_db.load_table(
            workflow.get_data_frame_upload_table_name()
        )
    except Exception:
        return render(
            request,
            'error.html',
            {'message': _('Exception while retrieving the data frame')})

    # Update the data frame
    status = ops.perform_dataframe_upload_merge(workflow,
                                                existing_df,
                                                data_frame,
                                                upload_data)

    if status:
        # Something went wrong. Flag it and reload
        context = {'form': form,
                   'wid': workflow.id,
                   'prev_step': upload_data['step_1'],
                   'valuerange': range(5) if workflow.has_table() else range(3),
                   'df_info': df_info}
        return render(request, 'dataops/upload_s2.html', context)

    # Nuke the temporary table
    pandas_db.delete_upload_table(workflow.get_data_frame_upload_table_name())

    # Log the event
    col_info = workflow.get_column_info()
    Log.objects.register(request.user,
                         Log.WORKFLOW_DATA_UPLOAD,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'num_rows': workflow.nrows,
                          'num_cols': workflow.ncols,
                          'column_names': col_info[0],
                          'column_types': col_info[1],
                          'column_unique': col_info[2]})

    # Go back to show the workflow detail
    return redirect(reverse('table:display'))


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

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    CREATES:

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Key column name selected in DST

    src_selected_key: Key column name selected in SRC

    how_merge: How to merge. One of {left, right, outter, inner}

    :param request: Web request
    :return: the dictionary upload_data in the session object
    """
    # Get the workflow id we are processing
    workflow = get_workflow(request, prefetch_related='columns')
    if not workflow:
        return redirect('home')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect('dataops:uploadmerge')

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
    src_is_key_column = upload_data['src_is_key_column']
    src_unique_col_names = [v for x, v in enumerate(src_column_names)
                            if src_is_key_column[x] and columns_to_upload[x]]

    # Bind the form with the received data (remember unique columns and
    # preselected keys.)'
    form = SelectKeysForm(
        request.POST or None,
        dst_keys=dst_unique_col_names,
        src_keys=src_unique_col_names,
        src_selected_key=upload_data.get('src_selected_key', None),
        dst_selected_key=upload_data.get('dst_selected_key', None),
        how_merge=upload_data.get('how_merge', None)
    )

    # Process the initial loading of the form
    if request.method != 'POST':
        # Update the dictionary with the session information
        request.session['upload_data'] = upload_data
        return render(
            request, 'dataops/upload_s3.html',
            {'form': form,
             'valuerange': range(5),
             'prev_step': reverse('dataops:upload_s2'),
             'wid': workflow.id})

    # We are processing a post request with the information given by the user

    # If the form is not valid, re-visit (nothing is checked so far...)
    if not form.is_valid():
        return render(
            request, 'dataops/upload_s3.html',
            {'form': form,
             'valuerange': range(5),
             'prev_step': reverse('dataops:upload_s3')})

    # Get the keys and merge method and store them in the session dict
    upload_data['dst_selected_key'] = form.cleaned_data['dst_key']
    upload_data['src_selected_key'] = form.cleaned_data['src_key']
    upload_data['how_merge'] = form.cleaned_data['how_merge']

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

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Key column name selected in DST

    src_selected_key: Key column name selected in SRC

    how_merge: How to merge. One of {left, right, outter, inner}

    :param request: Web request
    :return:
    """
    # Get the workflow id we are processing
    workflow = get_workflow(request, prefetch_related='columns')
    if not workflow:
        return redirect('home')

    # Get the dictionary containing the information about the upload
    upload_data = request.session.get('upload_data', None)
    if not upload_data:
        # If there is nsendo object, someone is trying to jump directly here.
        return redirect('dataops:uploadmerge')

    # Check the type of request that is being processed
    if request.method == 'POST':
        # We are processing a POST request

        # Get the dataframes to merge
        try:
            dst_df = pandas_db.load_from_db(
                workflow.get_data_frame_table_name()
            )
            src_df = pandas_db.load_from_db(
                workflow.get_data_frame_upload_table_name()
            )
        except Exception:
            return render(request,
                          'error.html',
                          {'message': _('Exception while loading data frame')})

        # Performing the merge
        status = ops.perform_dataframe_upload_merge(workflow,
                                                    dst_df,
                                                    src_df,
                                                    upload_data)

        # Nuke the temporary table
        pandas_db.delete_upload_table(
            workflow.get_data_frame_upload_table_name()
        )

        col_info = workflow.get_column_info()
        if status:
            Log.objects.register(request.user,
                                 Log.WORKFLOW_DATA_FAILEDMERGE,
                                 workflow,
                                 {'id': workflow.id,
                                  'name': workflow.name,
                                  'num_rows': workflow.nrows,
                                  'num_cols': workflow.ncols,
                                  'column_names': col_info[0],
                                  'column_types': col_info[1],
                                  'column_unique': col_info[2],
                                  'error_msg': status})

            messages.error(request, _('Merge operation failed. ') + status),
            return redirect(reverse('table:display'))

        # Log the event
        Log.objects.register(request.user,
                             Log.WORKFLOW_DATA_MERGE,
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

        return redirect(reverse('table:display'))

    # We are processing a GET request

    # Create the information to include in the final report table
    dst_column_names = upload_data['dst_column_names']
    dst_selected_key = upload_data['dst_selected_key']
    src_selected_key = upload_data['src_selected_key']
    # List of final column names
    final_columns = sorted(set().union(
        dst_column_names,
        upload_data['rename_column_names']
    ))
    # Dictionary with (new src column name: (old name, is_uploaded?)
    src_info = {x: (y, z) for (x, y, z) in zip(
        upload_data['rename_column_names'],
        upload_data['initial_column_names'],
        upload_data['columns_to_upload']
    )}

    # Create the strings to show in the table for each of the rows explaining
    # what is going to be the effect of the update operation over them.
    #
    # There are 8 cases depending on the column name being a key column,
    # in DST, SRC, if SRC is being renamed, and SRC is being loaded.
    #
    # Case 1: The column is the key column used for the merge (skip it)
    #
    # Case 2: in DST, NOT in SRC:
    #         Dst | |
    #
    # Case 3: in DST, in SRC, NOT LOADED
    #         Dst Name | <-- | Src new name (Ignored)
    #
    # Case 4: NOT in DST, in SRC, NOT LOADED
    #         | | Src new name (Ignored)
    #
    # Case 5: in DST, in SRC, Loaded, no rename:
    #         Dst Name (Update) | <-- | Src name
    #
    # Case 6: in DST, in SRC, loaded, rename:
    #         Dst Name (Update) | <-- | Src new name (Renamed)
    #
    # Case 7: NOT in DST, in SRC, loaded, no rename
    #         Dst Name (NEW) | <-- | src name
    #
    # Case 8: NOT in DST, in SRC, loaded, renamed
    #         Dst Name (NEW) | <-- | src name (renamed)
    #
    info = []
    for colname in final_columns:

        # Case 1: Skip the keys
        if colname == src_selected_key or colname == dst_selected_key:
            continue

        # Case 2: Column is in DST and left untouched (no counter part in SRC)
        if colname not in list(src_info.keys()):
            info.append((colname, False, ''))
            continue

        # Get old name and if it is going to be loaded
        old_name, to_load = src_info[colname]

        # Column is not going to be loaded anyway
        if not to_load:
            if colname in dst_column_names:
                # Case 3
                info.append((colname, False, colname + _(' (Ignored)')))
            else:
                # Case 4
                info.append(('', False, colname + _(' (Ignored)')))
            continue

        # Initial name on the dst data frame
        dst_name = colname
        # Column not present in DST, so it is a new column
        if colname not in dst_column_names:
            dst_name += _(' (New)')
        else:
            dst_name += _(' (Update)')

        src_name = colname
        if colname != old_name:
            src_name += _(' (Renamed)')

        # Cases 5 - 8
        info.append((dst_name, True, src_name))

    # Store the value in the request object and update
    request.session['upload_data'] = upload_data

    return render(request, 'dataops/upload_s4.html',
                  {'prev_step': reverse('dataops:upload_s3'),
                   'info': info,
                   'valuerange': range(5),
                   'next_name': 'Finish'})
