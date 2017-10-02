# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import Counter
import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from logs import ops
from workflow.models import Workflow
from ontask import is_instructor, slugify
from .forms import UploadFileForm, SelectColumnForm, SelectUniqueKeysForm

import pandas as pd

import panda_db


@login_required
@user_passes_test(is_instructor)
def dataops(request):
    workflow_id = request.session.get('ontask_workflow_id', None)
    if workflow_id is None:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    get_object_or_404(Workflow, pk=workflow_id)

    return render(request, 'dataops/data_ops.html')


@login_required
@user_passes_test(is_instructor)
def csvupload1(request):
    """
    The four step process will populate the following dictionary with name
    csv_upload_data:

    columns_to_uplload: Boolean list denoting the columns in SRC that are
                        marked for upload.

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_selected_key: Unique column name selected in DST

    src_is_unique_column: Boolean list with src columns that are unique

    src_selected_key: Unique column name selected in SRC

    how_merge: How to merge. One of {left, right, outter, inner}

    how_dup_columns: How to handle column overlap

    initial_column_names: List of column names in the CSV file.

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    autorename_column_names: Automatically modified column names

    override_columns_names: Names of dst columns that will be overridden in

    :param request: Web request
    :return:
    """

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    csv_upload_data = {}
    request.session['csv_upload_data'] = csv_upload_data

    workflow_id = request.session.get('ontask_workflow_id', None)
    if workflow_id is None:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    get_object_or_404(Workflow, pk=workflow_id)

    # Bind the form with the received data
    form = UploadFileForm(request.POST or None, request.FILES or None)

    # Process the initial loading of the form
    if request.method != 'POST':
        return render(request, 'dataops/csvupload1.html',
                      {'form': form,
                       'wid': workflow_id,
                       'prev_step': reverse('dataops:list')})

    # Process the reception of the file
    if not form.is_multipart():
        msg = "CSV upload form is not multiform"
        context = {'message': msg}

        meta = request.META.get('HTTP_REFERER', None)
        if meta:
            context['meta'] = meta
        return render(request, 'critical_error.html', context=context)

    # If not valid, this is probably because the file submitted was too big
    if not form.is_valid():
        return render(request, 'error.html',
                      {'messages': form['file'].errors})

    # Process CSV file
    data_frame = None
    try:
        data_frame = pd.read_csv(request.FILES['file'],
                                 infer_datetime_format=True,
                                 parse_dates=True)
    except Exception, e:
        messages.error(request, 'Read operations failed.')
        render(request,
               'csvupload1.html',
               {'form': form,
                'prev_step': reverse('workflow:detail', args=[workflow_id]),
                'messages': messages})

    # If the frame has repeated column names, it will not be processed.
    if len(set(data_frame.columns)) != len(data_frame.columns):
        dup = [x for x, v in Counter(list(data_frame.columns)) if v > 1]
        messages.error(request,
                       'The file has duplicated column names (' +
                       ','.join(dup) + ').')
        return render(request, 'dataops/csvupload1.html',
                      {'form': form,
                       'prev_step': reverse('dataops:list')})

    # If the frame does not have any unique key, it is not very useful (no
    # way to uniquely identify rows. There must be at least one.
    src_is_unique_column = panda_db.are_unique_columns(data_frame)
    if not any(src_is_unique_column):
        messages.error(request,
                       'The data has no column with unique values per row. '
                       'At least one column must have unique values.')
        return render(request, 'dataops/csvupload1.html',
                      {'form': form,
                       'prev_step': reverse('dataops:list')})

    # Store this information in the csv_upload_data dictionary
    csv_upload_data['src_is_unique_column'] = src_is_unique_column

    # Store the data frame in the DB. This way, there is no need for us to
    # serialise it.
    panda_db.dump_upload_to_db(data_frame, workflow_id)

    return redirect(reverse('dataops:csvupload2'))


@login_required
@user_passes_test(is_instructor)
def csvupload2(request):

    workflow_id = request.session.get('ontask_workflow_id', None)
    if not workflow_id:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the dictionary to store information about the upload
    # is stored in the session.
    csv_upload_data = request.session.get('csv_upload_data', None)
    if csv_upload_data is None:
        # If there is no object, someone is trying to jump directly here.
        return redirect(reverse('dataops:csvupload1'))

    if settings.DEBUG:
        print('csv_upload_data', csv_upload_data)

    # Get the workflow that is being used to make sure it exists
    workflow = get_object_or_404(Workflow, pk=workflow_id)

    # Get the uploaded data_frame
    data_frame = None
    try:
        data_frame = panda_db.load_upload_from_db(workflow_id)
    except Exception, e:
        render(request,
               'error.html',
               {'message': 'Exception while retrieving the data frame'})

    # Get the column names from the data frame
    initial_columns = csv_upload_data.get('initial_column_names', None)
    if initial_columns is None:
        initial_columns = list(data_frame.columns)
        csv_upload_data['initial_column_names'] = initial_columns

    rename_column_names = csv_upload_data.get('rename_column_names', None)
    if rename_column_names is None:
        rename_column_names = [slugify(x) for x in initial_columns]
        csv_upload_data['rename_column_names'] = rename_column_names

    # List of Booleans identifying column names that are unique
    src_is_unique_column = csv_upload_data.get('src_is_unique_column', None)
    if src_is_unique_column is None:
        src_is_unique_column = panda_db.are_unique_columns(data_frame)
        csv_upload_data['src_is_unique_column'] = src_is_unique_column

    # List of booleans identifying columns to be uploaded
    columns_to_upload = csv_upload_data.get('columns_to_upload', None)
    if columns_to_upload is None:
        columns_to_upload = [False for _ in range(len(initial_columns))]
        csv_upload_data['columns_to_upload'] = columns_to_upload

    # Create one of the context elements for the form. Pack the lists so that
    # can be iterated in the template
    df_info = [list(i)
               for i in zip(panda_db.df_column_types_rename(data_frame),
                            src_is_unique_column,
                            initial_columns,
                            rename_column_names,
                            columns_to_upload)]

    # Bind the form with the received data (remember unique columns)
    form = SelectColumnForm(request.POST or None,
                            unique_columns=src_is_unique_column)

    first_upload = not panda_db.workflow_id_has_matrix(workflow_id)

    # Process the initial loading of the form
    if request.method != 'POST':
        # Update the dictionary with the session information
        request.session['csv_upload_data'] = csv_upload_data
        context = {'form': form,
                   'df_info': df_info,
                   'prev_step': reverse('dataops:csvupload1'),
                   'wid': workflow_id}
        if first_upload:
            context['next_name'] = 'Finish'
        return render(request, 'dataops/csvupload2.html', context)

    # If the form is not valid, re-visit
    if not form.is_valid():
        context = {'form': form,
                   'wid': workflow_id,
                   'prev_step': reverse('dataops:csvupload1'),
                   'df_info': df_info}
        if first_upload:
            context['next_name'] = 'Finish'
        return render(request, 'dataops/csvupload2.html', context)

    # We need to modify df_info with the information already in the post
    for i in range(len(initial_columns)):
        new_name = form.cleaned_data['new_name_%s' % i]
        df_info[i][2] = new_name
        csv_upload_data['rename_column_names'][i] = new_name
        upload = form.cleaned_data['upload_%s' % i]
        df_info[i][3] = upload
        csv_upload_data['columns_to_upload'][i] = upload

    # Update the dictionary with the session information
    request.session['csv_upload_data'] = csv_upload_data

    # Load the existing DF or None if it doesn't exist
    existing_df = panda_db.load_from_db(workflow_id)

    # If there is no existing_df, save the uploaded in the right place and
    # finish.
    if existing_df is None:
        # Update the data frame
        panda_db.perform_dataframe_upload_merge(workflow_id,
                                                existing_df,
                                                data_frame,
                                                csv_upload_data)

        # Log the event
        ops.put(request.user,
                'workflow_data_upload',
                workflow,
                {'id': workflow.id,
                 'name': workflow.name,
                 'num_rows': workflow.nrows,
                 'num_cols': workflow.ncols,
                 'column_names': json.loads(workflow.column_names),
                 'column_types': json.loads(workflow.column_types),
                 'column_unique': json.loads(workflow.column_unique)})

        # Go back to show the detail of the data frame
        return redirect(reverse('dataops:list'))

    return redirect(reverse('dataops:csvupload3'))


@login_required
@user_passes_test(is_instructor)
def csvupload3(request):

    # Get the dictionary to store information about the upload
    # is stored in the session.
    csv_upload_data = request.session.get('csv_upload_data', None)
    if not csv_upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect(reverse('dataops:csvupload1'))
    if settings.DEBUG:
        print('csv_upload_data', csv_upload_data)

    # Get the workflow id we are processing
    workflow_id = request.session.get('ontask_workflow_id', None)
    if not workflow_id:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    get_object_or_404(Workflow, pk=workflow_id)

    # Get the dst data_frame
    dst_df = None
    try:
        dst_df = panda_db.load_from_db(workflow_id)
    except Exception, e:
        render(request,
               'error.html',
               {'message': 'Exception while retrieving the data frame'})

    # Get column names in dst_df
    dst_column_names = csv_upload_data.get('dst_column_names', None)
    if not dst_column_names:
        dst_column_names = list(dst_df.columns)
        csv_upload_data['dst_column_names'] = dst_column_names

    # Array of booleans saying which columns are unique in the dst DF.
    dst_is_unique_column = csv_upload_data.get('dst_is_unique_column')
    if dst_is_unique_column is None:
        dst_is_unique_column = panda_db.are_unique_columns(dst_df)
        csv_upload_data['dst_is_unique_column'] = dst_is_unique_column

    # Array of unique col names in DST dataframe (insert in csv_upload_data)
    dst_unique_col_names = csv_upload_data.get('dst_unique_col_names', None)
    if dst_unique_col_names is None:
        dst_unique_col_names = [v for x, v in enumerate(dst_column_names)
                                if dst_is_unique_column[x]]
        csv_upload_data['dst_unique_col_names'] = dst_unique_col_names

    # Get column names of those with unique values
    columns_to_upload = csv_upload_data['columns_to_upload']
    src_column_names = csv_upload_data['rename_column_names']
    src_is_unique_column = csv_upload_data['src_is_unique_column']
    src_unique_col_names = [v for x, v in enumerate(src_column_names)
                            if src_is_unique_column[x] and columns_to_upload[x]]

    # Calculate the names of columns that overlap
    rename_column_names = csv_upload_data['rename_column_names']
    overlap_cols = (
        # DST Column names that are not Keys
        (set(dst_column_names) - set(dst_is_unique_column)) &
        # SRC Column names that are renamed, selected and not unique
        set([x for x, y, z in zip(rename_column_names,
                                  columns_to_upload,
                                  src_is_unique_column)
             if y and not z]))
    # Boolean capturing if there is column overlap
    are_overlap_cols = overlap_cols != set([])

    # Bind the form with the received data (remember unique columns and
    # preselected keys.)'
    form = SelectUniqueKeysForm(
        request.POST or None,
        dst_keys=dst_unique_col_names,
        src_keys=src_unique_col_names,
        src_selected_key=csv_upload_data.get('src_selected_key', None),
        dst_selected_key=csv_upload_data.get('dst_selected_key', None),
        how_merge=csv_upload_data.get('how_merge', None),
        how_dup_columns=csv_upload_data.get('how_dup_columns', None),
        are_overlap_cols=are_overlap_cols,
    )

    # Process the initial loading of the form
    if request.method != 'POST':
        # Update the dictionary with the session information
        request.session['csv_upload_data'] = csv_upload_data
        return render(request, 'dataops/csvupload3.html',
                      {'form': form,
                       'prev_step': reverse('dataops:csvupload2'),
                       'wid': workflow_id})

    # If the form is not valid, re-visit (nothing is checked so far...)
    if not form.is_valid():
        return render(request, 'dataops/csvupload3.html',
                      {'form': form,
                       'prev_step': reverse('dataops:csvupload3')})

    # TODO: Think deeper about this
    # Check if the merge returns zero rows to consider
    # Calculate the resulting number of rows
    # rows_before = dst_df.shape[0]
    # if csv_upload_data['how_merge'] == 'left':
    #     rows_after = dst_df.shape[0]
    # elif csv_upload_data['how_merge'] == 'right':
    #     rows_after = src_df.shape[0]
    # elif csv_upload_data['how_merge'] == 'outer':
    #     rows_after = len(set(dst_df[csv_upload_data['dst_selected_key']]) |
    #                      set(src_df[csv_upload_data['src_selected_key']]))
    # elif csv_upload_data['how_merge'] == 'inner':
    #     rows_after = len(set(dst_df[csv_upload_data['dst_selected_key']]) &
    #                      set(src_df[csv_upload_data['src_selected_key']]))
    # else:
    #     messages.error(request, 'Incorrect merge methods detected.')
    #     return render(request, 'critical_error.html', {})


    # Get the keys and merge method and store them in the session dict
    csv_upload_data['dst_selected_key'] = form.cleaned_data['dst_key']
    csv_upload_data['src_selected_key'] = form.cleaned_data['src_key']
    csv_upload_data['how_merge'] = form.cleaned_data['how_merge']
    csv_upload_data['how_dup_columns'] = \
        form.cleaned_data.get('how_dup_columns', None)

    # Check if there are overlapping columns
    autorename_column_names = []
    if are_overlap_cols:
        # check the value of how to handle the overlap
        how_dup_columns = form.cleaned_data.get('how_dup_columns', None)
        if how_dup_columns == 'rename':
            autorename_column_names = rename_column_names[:]
            # Columns must be renamed!
            for idx, col in enumerate(rename_column_names):
                # Skip the selected keys
                if col == csv_upload_data['src_selected_key']:
                    continue

                # If the column name is not in dst, no need to rename
                if col not in dst_column_names:
                    continue

                i = 0  # Suffix to rename
                while True:
                    i += 1
                    new_name = col + '_{0}'.format(i)
                    if new_name not in rename_column_names and \
                       new_name not in dst_column_names:
                        break
                autorename_column_names[idx] = new_name
    csv_upload_data['autorename_column_names'] = autorename_column_names

    request.session['csv_upload_data'] = csv_upload_data

    return redirect(reverse('dataops:csvupload4'))


@login_required
@user_passes_test(is_instructor)
def csvupload4(request):

    # Get the dictionary to store information about the upload
    # is stored in the session.
    csv_upload_data = request.session.get('csv_upload_data', None)
    if not csv_upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect(reverse('dataops:csvupload1'))
    if settings.DEBUG:
        print('csv_upload_data', csv_upload_data)

    # Get the workflow id we are processing
    workflow_id = request.session.get('ontask_workflow_id', None)
    if not workflow_id:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    workflow = get_object_or_404(Workflow, pk=workflow_id)

    # Get the dst data_frame
    dst_df = None
    try:
        dst_df = panda_db.load_from_db(workflow_id)
    except Exception, e:
        render(request,
               'error.html',
               {'message': 'Exception while retrieving the data frame'})

    # Get the src data_frame to get the key column
    src_df = None
    try:
        src_df = panda_db.load_upload_from_db(workflow_id)
    except Exception, e:
        messages.error(request, 'Exception while retrieving the data frame')
        render(request, 'error.html', {})

    # Create the information to include in the final report table
    dst_column_names = csv_upload_data['dst_column_names']
    src_selected_key = csv_upload_data['src_selected_key']
    # Triplets to show in the page (dst column, Boolean saying there is some
    # change, and the message on the src colummn
    autorename_column_names = csv_upload_data['autorename_column_names']
    rename_column_names = csv_upload_data['rename_column_names']
    info = []
    initial_column_names = csv_upload_data['initial_column_names']

    # Names of the columns to override
    override_columns_names = set([])
    for idx, (x, y, z) in enumerate(zip(initial_column_names,
                                    rename_column_names,
                                    csv_upload_data['columns_to_upload'])):
        # There are several poosible cases
        #
        # 1) The unique key. No message needed because it is displayed at
        #    the top of the rows
        # 2) The column has not been selected. Simply show (Ignored) in the
        #    right.
        # 3) Column is selected and is NEW
        # 4) Column is selected and was renamed by the user
        # 5) Column is selected and was automatically renamed by the tool
        #    when requesting to preserve the overlapping columns

        # CASE 1: If it is a key
        if x == src_selected_key:
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
            if autorename_column_names and \
               autorename_column_names[idx] != y:
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
    csv_upload_data['override_columns_names'] = list(override_columns_names)

    if request.method != 'POST':
        request.session['csv_upload_data'] = csv_upload_data
        return render(request, 'dataops/csvupload4.html',
                      {'prev_step': reverse('dataops:csvupload3'),
                       'info': info,
                       'next_name': 'Finish'})

    # Processing the POST proceeding with the merge
    status = panda_db.perform_dataframe_upload_merge(workflow_id,
                                                     dst_df,
                                                     src_df,
                                                     csv_upload_data)

    if status:
        ops.put(request.user,
                'workflow_data_failedmerge',
                workflow,
                {'id': workflow.id,
                 'name': workflow.name,
                 'num_rows': workflow.nrows,
                 'num_cols': workflow.ncols,
                 'column_names': json.loads(workflow.column_names),
                 'column_types': json.loads(workflow.column_types),
                 'column_unique': json.loads(workflow.column_unique),
                 'error_msg': status})

        messages.error(request, 'Merge operation failed.'),
        return render(request, 'dataops/csvupload4.html',
                      {'prev_step': reverse('dataops:csvupload3'),
                       'next_name': 'Finish'})

    # Log the event
    ops.put(request.user,
            'workflow_data_merge',
            workflow,
            {'id': workflow.id,
             'name': workflow.name,
             'num_rows': workflow.nrows,
             'num_cols': workflow.ncols,
             'column_names': json.loads(workflow.column_names),
             'column_types': json.loads(workflow.column_types),
             'column_unique': json.loads(workflow.column_unique)})

    # Remove the csvupload from the session object
    request.session.pop('csv_upload_data', None)

    return redirect(reverse('dataops:list'))
