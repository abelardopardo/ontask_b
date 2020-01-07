# -*- coding: utf-8 -*-

"""Function to upload a data frame from an Athena connection object."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core import get_workflow, is_instructor
from ontask.dataops import forms


@user_passes_test(is_instructor)
@get_workflow()
def athenaupload_start(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Load a data frame using an Athena connection.

    The parameters are obtained and if valid, an operation is scheduled for
    execution.

    :param request: Web request
    :param pk: primary key of the Athena conn used
    :param workflow: Workflow being processed.
    :return: A page showing the low go view for status.
    """
    conn = models.AthenaConnection.objects.filter(
        pk=pk).filter(enabled=True).first()
    if not conn:
        return redirect(
            'dataops:athenaconns_instructor_index_instructor_index')

    form = forms.AthenaRequestConnectionParam(
        request.POST or None,
        workflow=workflow,
        instance=conn)

    if request.method == 'POST' and form.is_valid():
        run_params = form.get_field_dict()
        log_item = workflow.log(
            request.user,
            models.Log.WORKFLOW_DATA_ATHENA_UPLOAD,
            connection=conn.name,
            status='Preparing to execute')

        # Batch execution
        # athena_dataupload_task.delay(
        #     request.user.id,
        #     workflow.id,
        #     conn.id,
        #     run_params,
        #     log_item.id)

        # Show log execution
        return render(
            request,
            'dataops/operation_done.html',
            {'log_id': log_item.id, 'back_url': reverse('table:display')})

    return render(
        request,
        'dataops/athenaupload_start.html',
        {
            'form': form,
            'wid': workflow.id,
            'dtype': 'Athena',
            'dtype_select': _('Athena connection'),
            'connection': conn,
            'valuerange': range(5) if workflow.has_table() else range(3),
            'prev_step': reverse('dataops:athenaconns_instructor_index')})
