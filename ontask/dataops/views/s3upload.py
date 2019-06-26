# -*- coding: utf-8 -*-

"""View for the initial step to load data from an S3 bucket."""

from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ontask.dataops.forms import UploadS3FileForm
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.workflow.models import Workflow


@user_passes_test(is_instructor)
@get_workflow()
def s3upload_start(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Upload the S3 data as first step.

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
    # Bind the form with the received data
    form = UploadS3FileForm(
        request.POST or None,
        request.FILES or None,
        workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Dictionary to populate gradually throughout the sequence of steps. It
        # is stored in the session.
        request.session['upload_data'] = {
            'initial_column_names': form.frame_info[0],
            'column_types': form.frame_info[1],
            'src_is_key_column': form.frame_info[2],
            'step_1': reverse('dataops:csvupload_start')}

        return redirect('dataops:upload_s2')

    return render(
        request,
        'dataops/upload1.html',
        {
            'form': form,
            'wid': workflow.id,
            'dtype': 'S3 CSV',
            'dtype_select': _('S3 CSV file'),
            'valuerange': range(5) if workflow.has_table() else range(3),
            'prev_step': reverse('dataops:uploadmerge')})
