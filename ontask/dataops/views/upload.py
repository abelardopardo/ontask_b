# -*- coding: utf-8 -*-

"""Views for steps 2 - 4 of the upload process."""
from builtins import range, zip
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from ontask import models
from ontask.core import get_workflow, is_instructor
from ontask.dataops import forms, services


@user_passes_test(is_instructor)
@get_workflow()
def uploadmerge(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Show the table of options for upload/merge operation.

    :param request: Http Request
    :param workflow: To know if this is upload or merge.
    :return: Nothing
    """
    # Get the workflow that is being used
    return render(
        request,
        'dataops/uploadmerge.html',
        {
            'valuerange': range(5) if workflow.has_table() else range(3),
            'sql_enabled': models.SQLConnection.objects.filter(
                enabled=True).count() > 0,
            'athena_enabled': models.AthenaConnection.objects.filter(
                enabled=True).count() > 0})


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def upload_s2(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Second step of the upload process.

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
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: the dictionary upload_data in the session object
    """
    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data')
    if not upload_data:
        # If there is no object, or it is an empty dict, it denotes a direct
        # jump to this step, get back to the dataops page
        return redirect('dataops:uploadmerge')

    # Get the column names, types, and those that are unique from the data
    # frame
    try:
        initial_columns = upload_data.get('initial_column_names')
        column_types = upload_data.get('column_types')
        src_is_key_column = upload_data.get('src_is_key_column')
    except KeyError:
        # The page has been invoked out of order
        return redirect(upload_data.get(
            'step_1',
            reverse('dataops:uploadmerge')))

    # Get or create the list with the renamed column names
    rename_column_names = upload_data.get('rename_column_names')
    if rename_column_names is None:
        rename_column_names = initial_columns[:]
        upload_data['rename_column_names'] = rename_column_names

    # Get or create list of booleans identifying columns to be uploaded
    columns_to_upload = upload_data.get('columns_to_upload')
    if columns_to_upload is None:
        columns_to_upload = [True] * len(initial_columns)
        upload_data['columns_to_upload'] = columns_to_upload

    # Get or create list of booleans identifying key columns to be kept
    keep_key_column = upload_data.get('keep_key_column')
    if keep_key_column is None:
        keep_key_column = upload_data['src_is_key_column'][:]
        upload_data['keep_key_column'] = keep_key_column

    # Bind the form with the received data (remember unique columns)
    form = forms.SelectColumnUploadForm(
        request.POST or None,
        column_names=rename_column_names,
        columns_to_upload=columns_to_upload,
        is_key=src_is_key_column,
        keep_key=keep_key_column,
    )

    # Get a hold of the fields to create a list to be processed in the page
    load_fields = [
        ffield for ffield in form if ffield.name.startswith('upload_')]
    newname_fields = [
        ffield for ffield in form if ffield.name.startswith('new_name_')]
    src_key_fields = [
        form['make_key_%s' % idx] if src_is_key_column[idx] else None
        for idx in range(len(src_is_key_column))
    ]

    # Create one of the context elements for the form. Pack the lists so that
    # they can be iterated in the template
    df_info = [list(info_item) for info_item in zip(
        load_fields,
        initial_columns,
        newname_fields,
        column_types,
        src_key_fields)]

    if request.method == 'POST' and form.is_valid():
        try:
            return services.upload_step_two(
                request,
                workflow,
                form.cleaned_data,
                upload_data)
        except Exception as exc:
            # Something went wrong. Flag it and reload
            messages.error(
                request,
                _('Unable to upload the data: {0}').format(str(exc)),
            )
            return redirect('dataops:uploadmerge')

    # Update the dictionary with the session information
    request.session['upload_data'] = upload_data
    context = {
        'form': form,
        'wid': workflow.id,
        'prev_step': upload_data['step_1'],
        'valuerange': range(5) if workflow.has_table() else range(3),
        'df_info': df_info,
        'next_name': None}

    if not workflow.has_table():
        # It is an upload, not a merge, set the next step to finish
        context['next_name'] = _('Finish')
    return render(request, 'dataops/upload_s2.html', context)


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def upload_s3(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Step 3: This is already a merge operation (not an upload).

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
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: the dictionary upload_data in the session object
    """
    # Get the dictionary to store information about the upload
    # is stored in the session.
    upload_data = request.session.get('upload_data')
    if not upload_data:
        # If there is no object, someone is trying to jump directly here.
        return redirect('dataops:uploadmerge')

    # Get column names in dst_df
    dst_column_names = upload_data.get('dst_column_names')
    if not dst_column_names:
        dst_column_names = workflow.get_column_names()
        upload_data['dst_column_names'] = dst_column_names

    # Array of booleans saying which columns are unique in the dst DF.
    dst_is_unique_column = upload_data.get('dst_is_unique_column')
    if dst_is_unique_column is None:
        dst_is_unique_column = workflow.get_column_unique()
        upload_data['dst_is_unique_column'] = dst_is_unique_column

    # Array of unique col names in DST
    dst_unique_col_names = upload_data.get('dst_unique_col_names')
    if dst_unique_col_names is None:
        dst_unique_col_names = [
            cname for idx, cname in enumerate(dst_column_names)
            if dst_is_unique_column[idx]]
        upload_data['dst_unique_col_names'] = dst_unique_col_names

    # Get the names of he unique columns to upload in the source DF
    columns_to_upload = upload_data['columns_to_upload']
    src_column_names = upload_data['rename_column_names']
    src_is_key_column = upload_data['src_is_key_column']
    src_unique_col_names = [
        cname for idx, cname in enumerate(src_column_names)
        if src_is_key_column[idx] and columns_to_upload[idx]]

    # Bind the form with the received data (remember unique columns and
    # preselected keys.)'
    form = forms.SelectKeysForm(
        request.POST or None,
        dst_keys=dst_unique_col_names,
        src_keys=src_unique_col_names,
        src_selected_key=upload_data.get('src_selected_key'),
        dst_selected_key=upload_data.get('dst_selected_key'),
        how_merge=upload_data.get('how_merge'),
    )

    if request.method == 'POST' and form.is_valid():
        # Get the keys and merge method and store them in the session dict
        upload_data['dst_selected_key'] = form.cleaned_data['dst_key']
        upload_data['src_selected_key'] = form.cleaned_data['src_key']
        upload_data['how_merge'] = form.cleaned_data['how_merge']

        # Update session object
        request.session['upload_data'] = upload_data

        return redirect('dataops:upload_s4')

    return render(
        request,
        'dataops/upload_s3.html',
        {
            'form': form,
            'valuerange': range(5),
            'prev_step': reverse('dataops:upload_s2')})


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def upload_s4(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Step 4: Show the user the expected effect of the merge and perform it.

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
    :param workflow: Workflow being manipulated (set by the decorators)
    :return:
    """
    # Get the dictionary containing the information about the upload
    upload_data = request.session.get('upload_data')
    if not upload_data:
        # If there is nsendo object, someone is trying to jump directly here.
        return redirect('dataops:uploadmerge')

    # Check the type of request that is being processed
    if request.method == 'POST':
        return services.upload_step_four(
            request,
            workflow,
            upload_data)

    column_info = services.upload_prepare_step_four(upload_data)

    # Store the value in the request object and update
    request.session['upload_data'] = upload_data

    return render(
        request,
        'dataops/upload_s4.html',
        {
            'prev_step': reverse('dataops:upload_s3'),
            'info': column_info,
            'valuerange': range(5),
            'next_name': 'Finish'})
