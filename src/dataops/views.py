# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render, reverse

import logs.ops
from dataops import pandas_db, ops
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .forms import RowFilterForm, RowForm, field_prefix


@user_passes_test(is_instructor)
def dataops(request):
    # Get the workflow that is being used
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Make sure there is no upload table in the db for this workflow
    if ops.workflow_has_upload_table(workflow):
        pandas_db.delete_upload_table(workflow.id)

    return render(request, 'dataops/data_ops.html', {})


@user_passes_test(is_instructor)
def uploadmerge(request):
    return render(request, 'dataops/uploadmerge.html', {})


@user_passes_test(is_instructor)
def row_update(request):
    """
    Receives a POST request to update a row in the data table
    :param request: Request object with all the data.
    :return:
    """

    # If there is no workflow object, go back to the index
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # If the workflow has no data, something went wrong, go back to the
    # dataops home
    if workflow.nrows == 0:
        return redirect('dataops:list')

    # Get the pair key,value to fetch the row from the table
    update_key = request.GET.get('update_key', None)
    update_val = request.GET.get('update_val', None)

    if not update_key or not update_val:
        # Malformed request
        return render(request, 'error.html',
                      {'message': 'Unable to update table row'})

    # Get the rows from the table
    rows = pandas_db.execute_select_on_table(workflow.id,
                                             [update_key],
                                             [update_val])

    row_form = RowForm(request.POST or None,
                       workflow=workflow,
                       initial_values=list(rows[0]))

    if request.method == 'GET' or not row_form.is_valid():
        return render(request,
                      'dataops/row_filter.html',
                      {'workflow': workflow,
                       'row_form': row_form,
                       'cancel_url': reverse('table:display')})

    # This is a valid POST request

    # Create the query to update the row
    set_fields = []
    set_values = []
    columns = workflow.get_columns()
    unique_names = [c.name for c in columns if c.is_key]
    unique_field = None
    unique_value = None
    log_payload = []
    for idx, col in enumerate(columns):
        value = row_form.cleaned_data[field_prefix + '%s' % idx]
        set_fields.append(col.name)
        set_values.append(value)
        log_payload.append((col.name, str(value)))

        if not unique_field and col.name in unique_names:
            unique_field = col.name
            unique_value = value

    # If there is no unique key, something went wrong.
    if not unique_field:
        raise Exception('Key value not found when updating row')

    pandas_db.update_row(workflow.id,
                         set_fields,
                         set_values,
                         [unique_field],
                         [unique_value])

    # Log the event
    logs.ops.put(request.user,
                 'tablerow_update',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'new_values': log_payload})

    return redirect('table:display')


@user_passes_test(is_instructor)
def row_create(request):
    """
    Receives a POST request to create a new row in the data table
    :param request: Request object with all the data.
    :return:
    """

    # If there is no workflow object, go back to the index
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # If the workflow has no data, the operation should not be allowed
    if workflow.nrows == 0:
        return redirect('dataops:list')

    # Create the form
    form = RowForm(request.POST or None, workflow=workflow)

    if request.method == 'GET' or not form.is_valid():
        return render(request,
                      'dataops/row_create.html',
                      {'workflow': workflow,
                       'form': form,
                       'cancel_url': reverse('table:display')})

    # Create the query to update the row
    columns = workflow.get_columns()
    column_names = [c.name for c in columns]
    field_name = field_prefix + '%s'
    row_vals = [form.cleaned_data[field_name % idx]
                for idx in range(len(columns))]

    # Load the existing df from the db
    df = pandas_db.load_from_db(workflow.id)

    # Perform the row addition in the DF first
    # df2 = pd.DataFrame([[5, 6], [7, 8]], columns=list('AB'))
    # df.append(df2, ignore_index=True)
    new_row = pd.DataFrame([row_vals], columns=column_names)
    df = df.append(new_row, ignore_index=True)

    # Verify that the unique columns remain unique
    for ucol in [c for c in columns if c.is_key]:
        if not ops.is_unique_column(df[ucol.name]):
            form.add_error(
                None,
                'Repeated value in column ' + ucol.name + '.' +
                ' It must be different to maintain Key property'
            )
            return render(request,
                          'dataops/row_create.html',
                          {'workflow': workflow,
                           'form': form,
                           'cancel_url': reverse('table:display')})

    # Restore the dataframe to the DB
    ops.store_dataframe_in_db(df, workflow.id)

    # Log the event
    log_payload = zip(column_names, [str(x) for x in row_vals])
    logs.ops.put(request.user,
                 'tablerow_create',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'new_values': log_payload})

    # Done. Back to the table view
    return redirect('table:display')

