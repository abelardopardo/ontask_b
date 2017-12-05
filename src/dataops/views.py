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

    return render(request, 'dataops/data_ops.html', {})


@user_passes_test(is_instructor)
def uploadmerge(request):
    return render(request, 'dataops/uploadmerge.html', {})


@user_passes_test(is_instructor)
def row_filter(request):
    # Get the workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Add to context for rendering the title
    context = {'workflow': workflow,
               'cancel_url': reverse('dataops:list')}

    # If the workflow does not have any rows, there is no point on doing this.
    if workflow.nrows == 0:
        return render(request, 'dataops/row_filter.html', context)

    # Fetch the information for the search form regardless
    form = RowFilterForm(request.POST or None, workflow=workflow)

    # This form is always rendered, so it is included in the context anyway
    context['form'] = form

    if request.method != 'POST':
        return render(request, 'dataops/row_filter.html', context)

    # Processing now a POST request (it could be of two types!)

    if request.POST.get('submit') == 'update':
        # This is the case in which the row is updated
        row_form = RowForm(request.POST, workflow=workflow)
        if row_form.is_valid() and row_form.has_changed():
            # Update content in the DB
            set_fields = []
            set_values = []
            where_field = None
            where_value = None
            log_payload = []
            # Create the SET name = value part of the query
            for idx, column in enumerate(workflow.columns.all()):
                value = row_form.cleaned_data[column.name]
                if column.is_key:
                    if not where_field:
                        # Remember one unique key for selecting the row
                        where_field = column.name
                        where_value = value
                    continue

                set_fields.append(column.name)
                set_values.append(value)
                log_payload.append((column.name, value))

            pandas_db.update_row(workflow.id,
                                 set_fields,
                                 set_values,
                                 [where_field],
                                 [where_value])

            # Log the event
            logs.ops.put(request.user,
                         'tablerow_update',
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'new_values': log_payload})

            # Change is done.
    else:
        if form.is_valid():
            # Request is a POST of the SEARCH (first form)
            where_field = []
            where_value = []
            for name in form.key_names:
                value = form.cleaned_data[name]
                if value:
                    # Remember the value of the key
                    where_field = name
                    where_value = value
                    break

            # Get the row from the table
            rows = pandas_db.execute_select_on_table(workflow.id,
                                                     [where_field],
                                                     [where_value])

            if len(rows) == 1:
                # A single row has been selected. Create and pre-populate
                # the update form
                row_form = RowForm(None,
                                   workflow=workflow,
                                   initial_values=list(rows[0]))
                context['row_form'] = row_form
            else:
                form.add_error(None, 'No data found with the given keys')

    return render(request, 'dataops/row_filter.html', context)


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
    # rowfilter page
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

    # This method can only be invoked through a POST operation
    if request.method == 'GET':
        # Get the row form and render the page
        row_form = RowForm(None,
                           workflow=workflow,
                           initial_values=list(rows[0]))

        return render(request,
                      'dataops/row_filter.html',
                      {'workflow': workflow,
                       'row_form': row_form,
                       'cancel_url': reverse('table:display')})

    # This is A POST request

    # Initialise the form
    row_form = RowForm(request.POST,
                       workflow=workflow,
                       initial_values=list(rows[0]))

    # If the form was not valid, something went wrong
    if not row_form.is_valid():
        return redirect('dataops:rowupdate')

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
        raise Exception('Unique key not found when updating row')

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

    if request.method == 'POST':

        # If the form is valid proceed with the operation
        if form.is_valid():
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
                        ucol.name,
                        'Value in column ' + ucol.name + ' is in another row.' +
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
            log_payload = zip(column_names, row_vals)
            logs.ops.put(request.user,
                         'tablerow_create',
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'new_values': log_payload})

            # Done. Back to the table view
            return redirect('table:display')

    return render(request,
                  'dataops/row_create.html',
                  {'workflow': workflow,
                   'form': form,
                   'cancel_url': reverse('table:display')})
