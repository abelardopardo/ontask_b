# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from collections import Counter

import pandas as pd
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse

from dataops import ops
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .forms import UploadExcelFileForm


@user_passes_test(is_instructor)
def excelupload1(request):
    """
    Step 1 of the whole process to read data into the platform.

    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    :param request: Web request
    :return: Creates the upload_data dictionary in the session
    """

    # Get the current workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Bind the form with the received data
    form = UploadExcelFileForm(request.POST or None, request.FILES or None)

    # Process the initial loading of the form
    if request.method != 'POST':
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'wid': workflow.id,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Process the reception of the file
    if not form.is_multipart():
        msg = "Excel upload form is not multiform"
        context = {'message': msg}

        meta = request.META.get('HTTP_REFERER', None)
        if meta:
            context['meta'] = meta
        return render(request, 'critical_error.html', context=context)

    # If not valid, this is probably because the file submitted was too big
    if not form.is_valid():
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'wid': workflow.id,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Process Excel file using pandas read_excel
    try:
        data_frame = pd.read_excel(
            request.FILES['file'],
            sheetname=form.cleaned_data['sheet'],
            index_col=False,
            infer_datetime_format=True,
            quotechar='"',
        )

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
    except Exception as e:
        form.add_error('file',
                       'File could not be processed ({0})'.format(e.message))
        return render(request,
                      'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # If the frame has repeated column names, it will not be processed.
    if len(set(data_frame.columns)) != len(data_frame.columns):
        dup = [x for x, v in Counter(list(data_frame.columns)) if v > 1]
        form.add_error(
            'file',
            'The file has duplicated column names (' +
            ','.join(dup) + ').')
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # If the data frame does not have any unique key, it is not useful (no
    # way to uniquely identify rows). There must be at least one.
    src_is_key_column = ops.are_unique_columns(data_frame)
    if not any(src_is_key_column):
        form.add_error(
            'file',
            'The data has no column with unique values per row. '
            'At least one column must have unique values.')
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Store the data frame in the DB.
    try:
        # Get frame info with three lists: names, types and is_key
        frame_info = ops.store_upload_dataframe_in_db(data_frame, workflow.id)
    except Exception as e:
        form.add_error(
            'file',
            'Sorry. This file cannot be processed.'
        )
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Excel',
                       'dtype_select': 'Excel file',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    request.session['upload_data'] = {
        'initial_column_names': frame_info[0],
        'column_types': frame_info[1],
        'src_is_key_column': frame_info[2],
        'step_1': reverse('dataops:excelupload1')
    }

    return redirect('dataops:upload_s2')
