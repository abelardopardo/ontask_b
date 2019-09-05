# -*- coding: utf-8 -*-

"""Function to upload a data frame from an existing SQL connection object."""

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
from ontask.dataops.forms import SQLRequestPassword, load_df_from_sqlconnection
from ontask.dataops.pandas import store_temporary_dataframe, verify_data_frame
from ontask.models import SQLConnection, Workflow


@user_passes_test(is_instructor)
@get_workflow()
def sqlupload_start(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
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
    :return: Creates the upload_data dictionary in the session
    """
    conn = SQLConnection.objects.filter(pk=pk).first()
    if not conn:
        return redirect('dataops:sqlconns_instructor_index_instructor_index')

    form = None
    if conn.db_password:
        # The connection needs a password  to operate
        form = SQLRequestPassword(request.POST or None)

    context = {
        'form': form,
        'wid': workflow.id,
        'dtype': 'SQL',
        'dtype_select': _('SQL connection'),
        'valuerange': range(5) if workflow.has_table() else range(3),
        'prev_step': reverse('dataops:sqlconns_instructor_index'),
        'conn_type': conn.conn_type,
        'conn_driver': conn.conn_driver,
        'db_user': conn.db_user,
        'db_passwd': _('<PROTECTED>') if conn.db_password else '',
        'db_host': conn.db_host,
        'db_port': conn.db_port,
        'db_name': conn.db_name,
        'db_table': conn.db_table}

    if request.method == 'POST' and (not form or form.is_valid()):
        read_pwd = None
        if form:
            read_pwd = form.cleaned_data['password']

        # Process SQL connection using pandas
        try:
            data_frame = load_df_from_sqlconnection(
                conn,
                read_pwd)
            # Verify the data frame
            verify_data_frame(data_frame)
        except OnTaskDataFrameNoKey as exc:
            messages.error(request, str(exc))
            return render(request, 'dataops/sqlupload_start.html', context)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to obtain data: {0}').format(str(exc)))
            return render(request, 'dataops/sqlupload_start.html', context)

        # Store the data frame in the DB.
        try:
            # Get frame info with three lists: names, types and is_key
            frame_info = store_temporary_dataframe(
                data_frame,
                workflow)
        except Exception:
            form.add_error(
                None,
                _('The data from this connection cannot be processed.'),
            )
            return render(request, 'dataops/sqlupload_start.html', context)

        # Dictionary to populate gradually throughout the sequence of steps. It
        # is stored in the session.
        request.session['upload_data'] = {
            'initial_column_names': frame_info[0],
            'column_types': frame_info[1],
            'src_is_key_column': frame_info[2],
            'step_1': reverse(
                'dataops:sqlupload_start',
                kwargs={'pk': conn.id}),
        }

        return redirect('dataops:upload_s2')

    return render(request, 'dataops/sqlupload_start.html', context)
