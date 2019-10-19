# -*- coding: utf-8 -*-

"""Function to upload a data frame from an Athena connection object."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import OnTaskDataFrameNoKey
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.forms import (
    AthenaRequestConnectionParam, load_df_from_athenaconnection,
)
from ontask.dataops.pandas import store_temporary_dataframe, verify_data_frame
from ontask.models import AthenaConnection, Log, Workflow
from ontask.tasks import athena_dataupload_task


@user_passes_test(is_instructor)
@get_workflow()
def athenaupload_start(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Load a data frame using an Athena connection.

    The parameters are obtained and if valid, an operation is scheduled for
    execution.

    :param request: Web request
    :param pk: primary key of the Athena conn used
    :return: A page showing the low go view for status.
    """
    conn = AthenaConnection.objects.filter(
        pk=pk
    ).filter(enabled=True).first()
    if not conn:
        return redirect(
            'dataops:athenaconns_instructor_index_instructor_index')

    form = AthenaRequestConnectionParam(
        request.POST or None,
        workflow=workflow,
        instance=conn)

    context = {
        'form': form,
        'wid': workflow.id,
        'dtype': 'Athena',
        'dtype_select': _('Athena connection'),
        'connection': conn,
        'valuerange': range(5) if workflow.has_table() else range(3),
        'prev_step': reverse('dataops:athenaconns_instructor_index')}

    if request.method == 'POST' and form.is_valid():
        run_params = form.get_field_dict()
        log_item = workflow.log(
            request.user,
            Log.WORKFLOW_DATA_MERGE,
            connection=conn.name,
            status='Preparing to execute'
        )

        # Batch execution
        athena_dataupload_task.delay(
            request.user.id,
            workflow.id,
            conn.id,
            run_params,
            log_item.id)

        # Show log execution
        return render(
            request,
            'dataops/operation_done.html',
            {'log_id': log_item.id, 'back_url': reverse('table:display')})

    return render(request, 'dataops/athenaupload_start.html', context)
