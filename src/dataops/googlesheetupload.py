# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

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
        return redirect('home')

    # Bind the form with the received data
    form = UploadGoogleSheetForm(request.POST or None,
                                 request.FILES or None,
                                 workflow=workflow)

    # Process the initial loading of the form
    if request.method != 'POST':
        return render(
            request, 'dataops/upload1.html',
            {'form': form,
             'wid': workflow.id,
             'dtype': 'Google Sheet',
             'dtype_select': _('Google Sheet URL'),
             'valuerange': range(5) if workflow.has_table() else range(3),
             'prev_step': reverse('dataops:uploadmerge')})

    # If not valid, this is probably because the file submitted was too big
    if not form.is_valid():
        return render(
            request, 'dataops/upload1.html',
            {'form': form,
             'wid': workflow.id,
             'dtype': 'Google Sheet',
             'dtype_select': _('Google Sheet URL'),
             'valuerange': range(5) if workflow.has_table() else range(3),
             'prev_step': reverse('dataops:uploadmerge')})

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    request.session['upload_data'] = {
        'initial_column_names': form.frame_info[0],
        'column_types': form.frame_info[1],
        'src_is_key_column': form.frame_info[2],
        'step_1': reverse('dataops:googlesheetupload1')
    }

    return redirect('dataops:upload_s2')
