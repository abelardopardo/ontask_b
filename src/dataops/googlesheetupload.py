# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from collections import Counter
# Python 2 and 3: alternative 4
try:
    from urllib.parse import urlparse, urlencode, urlunparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse, urlunparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

import dataops.pandas_db
from dataops import ops, pandas_db
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .forms import UploadGoogleSheetForm


@user_passes_test(is_instructor)
def googlesheetupload1(request):
    """
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
    form = UploadGoogleSheetForm(request.POST or None, request.FILES or None)

    # Process the initial loading of the form
    if request.method != 'POST':
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'wid': workflow.id,
                       'dtype': 'Google Sheet',
                       'dtype_select': _('Google Sheet URL'),
                       'prev_step': reverse('dataops:uploadmerge')})

    # If not valid, this is probably because the file submitted was too big
    if not form.is_valid():
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'wid': workflow.id,
                       'dtype': 'Google Sheet',
                       'dtype_select': _('Google Sheet URL'),
                       'prev_step': reverse('dataops:uploadmerge')})

    # Process the URL provided by google. If the URL is obtained using the
    # GUI, it has as suffix /edit?[parameters]. This part needs to be replaced
    # by the suffix /export?format=csv
    # For example from:
    # https://docs.google.com/spreadsheets/d/DOCID/edit?usp=sharing
    # to
    # https://docs.google.com/spreadsheets/d/DOCID/export?format = csv&gid=0
    url_string = form.cleaned_data['google_url']
    parse_res = urlparse(url_string)
    if parse_res.path.endswith('/edit'):
        url_string = urlunparse([
            parse_res.scheme,
            parse_res.netloc,
            parse_res.path[:-len('/edit')] + '/export',
            parse_res.params,
            parse_res.query + '&format=csv',
            parse_res.fragment
        ])

    # Process the link using pandas read_csv
    try:
        data_frame = pandas_db.load_df_from_csvfile(
            url_string,
            form.cleaned_data['skip_lines_at_top'],
            form.cleaned_data['skip_lines_at_bottom'])
    except Exception as e:
        form.add_error(None,
                       _('File could not be processed ({0})').format(e.message))
        return render(request,
                      'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Google Sheet',
                       'dtype_select': 'Google Sheet URL',
                       'prev_step': reverse('dataops:uploadmerge')})

    # If the frame has repeated column names, it will not be processed.
    if len(set(data_frame.columns)) != len(data_frame.columns):
        dup = [x for x, v in Counter(list(data_frame.columns)) if v > 1]
        form.add_error(
            None,
            _('The file has duplicated column names') + ' (' +
            ','.join(dup) + ').')
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Google Sheet',
                       'dtype_select': 'Google Sheet URL',
                       'prev_step': reverse('dataops:uploadmerge')})

    # If the data frame does not have any unique key, it is not useful (no
    # way to uniquely identify rows). There must be at least one.
    src_is_key_column = dataops.pandas_db.are_unique_columns(data_frame)
    if not any(src_is_key_column):
        form.add_error(
            None,
            _('The data has no column with unique values per row. '
              'At least one column must have unique values.'))
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Google Sheet',
                       'dtype_select': 'Google Sheet URL',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Store the data frame in the DB.
    try:
        # Get frame info with three lists: names, types and is_key
        frame_info = ops.store_upload_dataframe_in_db(data_frame, workflow.id)
    except Exception as e:
        form.add_error(
            None,
            _('Sorry. This file cannot be processed.')
        )
        return render(request, 'dataops/upload1.html',
                      {'form': form,
                       'dtype': 'Google Sheet',
                       'dtype_select': 'Google Sheet URL',
                       'prev_step': reverse('dataops:uploadmerge')})

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    request.session['upload_data'] = {
        'initial_column_names': frame_info[0],
        'column_types': frame_info[1],
        'src_is_key_column': frame_info[2],
        'step_1': reverse('dataops:googlesheetupload1')
    }

    return redirect('dataops:upload_s2')
