# -*- coding: utf-8 -*-

"""Function to upload a data frame from an existing SQL connection object."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
import ontask.connection.forms
from ontask.core import get_workflow, is_instructor
from ontask.dataops import services


@user_passes_test(is_instructor)
@get_workflow()
def sqlupload_start(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Load a data frame using a SQL connection.

    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    :param request: Web request
    :param pk: primary key of the SQL conn used
    :param workflow: Workflow being used
    :return: Creates the upload_data dictionary in the session
    """
    conn = models.SQLConnection.objects.filter(
        pk=pk).filter(enabled=True).first()
    if not conn:
        return redirect('connection:sqlconns_index')

    form = None
    missing_field = conn.has_missing_fields()
    if missing_field:
        # The connection needs a password  to operate
        form = ontask.connection.forms.SQLRequestConnectionParam(
            request.POST or None,
            connection=conn)

    context = {
        'form': form,
        'wid': workflow.id,
        'dtype': 'SQL',
        'dtype_select': _('SQL connection'),
        'valuerange': range(5) if workflow.has_table() else range(3),
        'prev_step': reverse('connection:sqlconns_index'),
        'conn_type': conn.conn_type,
        'conn_driver': conn.conn_driver,
        'db_user': conn.db_user,
        'db_passwd': _('<PROTECTED>') if conn.db_password else '',
        'db_host': conn.db_host,
        'db_port': conn.db_port,
        'db_name': conn.db_name,
        'db_table': conn.db_table}

    if request.method == 'POST' and (not missing_field or form.is_valid()):
        if form:
            run_params = conn.get_missing_fields(form.cleaned_data)
        else:
            run_params = {}

        # Process SQL connection using pandas
        try:
            services.sql_upload_step_one(
                request,
                workflow,
                conn,
                run_params)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to obtain data: {0}').format(str(exc)))
            return render(request, 'dataops/sqlupload_start.html', context)

        return redirect('dataops:upload_s2')

    return render(request, 'dataops/sqlupload_start.html', context)
