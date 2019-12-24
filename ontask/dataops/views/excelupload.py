# -*- coding: utf-8 -*-

"""View to start the excelupload process."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core import get_workflow, is_instructor
from ontask.dataops import forms


@user_passes_test(is_instructor)
@get_workflow()
def excelupload_start(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Upload the Excel file as first step.

    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    :param request: Web request
    :param workflow: Workflow being used.
    :return: Creates the upload_data dictionary in the session
    """
    # Bind the form with the received data
    form = forms.UploadExcelFileForm(
        request.POST or None,
        request.FILES or None,
        workflow=workflow)

    # Process the reception of the file
    if not form.is_multipart():
        msg = _('Excel upload form is not multiform')
        context = {'message': msg}

        meta = request.META.get('HTTP_REFERER')
        if meta:
            context['meta'] = meta
        return render(request, 'critical_error.html', context=context)

    if request.method == 'POST' and form.is_valid():
        # Dictionary to populate gradually throughout the sequence of steps. It
        # is stored in the session.
        request.session['upload_data'] = {
            'initial_column_names': form.frame_info[0],
            'column_types': form.frame_info[1],
            'src_is_key_column': form.frame_info[2],
            'step_1': reverse('dataops:excelupload_start'),
            'log_upload': models.Log.WORKFLOW_DATA_EXCEL_UPLOAD}

        return redirect('dataops:upload_s2')

    return render(
        request,
        'dataops/upload1.html',
        {
            'form': form,
            'wid': workflow.id,
            'dtype': 'Excel',
            'dtype_select': 'Excel file',
            'valuerange': range(5) if workflow.has_table() else range(3),
            'prev_step': reverse('dataops:uploadmerge')})
