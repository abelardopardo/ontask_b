# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
import django_tables2 as tables

from workflow.models import Workflow
from dataops import panda_db
from ontask import is_instructor, slugify
from .forms import RowFilterForm, RowUpdateForm

@login_required
@user_passes_test(is_instructor)
def dataops(request):
    workflow_id = request.session.get('ontask_workflow_id', None)
    if workflow_id is None:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    get_object_or_404(Workflow, pk=workflow_id)

    return render(request, 'dataops/data_ops.html')


@login_required
@user_passes_test(is_instructor)
def row_filter(request):
    # Get the workflow object
    workflow = get_object_or_404(
        Workflow,
        pk=request.session.get('ontask_workflow_id', -1),
        user=request.user)

    # Add to context for rendering the title
    context = {'workflow': workflow}

    # If the workflow does not have any rows, there is no point on doing this.
    if workflow.nrows == 0:
        return render(request, 'dataops/row_filter.html', context)

    form = RowFilterForm(request.POST or None, workflow=workflow)
    context['form'] = form

    if request.method == 'POST':

        if form.is_valid():

            where_clause = []
            where_fields = []
            for name, type in zip(form.key_names, form.key_types):
                # None or '', skip
                if not form.cleaned_data[name]:
                    continue

                where_clause.append('{0} = %s'.format(name))
                where_fields.append(form.cleaned_data[name])

            if where_clause:
                where_clause = ' WHERE ' + ' AND '.join(where_clause)
            else:
                where_clause = None

            # Get the queryset from the matrix
            queryset = panda_db.execute_select_on_table(
                workflow.id,
                where_clause,
                where_fields
            )

            # If the queryset returned a single element, create the row form
            # and return
            if len(queryset) == 1:
                if request.POST['submit'] == 'submit':
                    row_form = RowUpdateForm(None,
                                             workflow=workflow,
                                             initial_values=list(queryset[0]))
                else:
                    row_form = RowUpdateForm(request.POST,
                                             workflow=workflow,
                                             initial_values=list(queryset[0]))
                    if row_form.is_valid() and row_form.has_changed():
                        # Update content in the DB
                        set_values = []
                        set_fields = []
                        for name, type in zip(row_form.col_names,
                                              row_form.col_types):

                            set_values.append('{0} = %s'.format(name))
                            set_fields.append(row_form.cleaned_data[name])


                        set_values = ' SET ' + ', '.join(set_values)
                        fields = set_fields + where_fields

                        # Update db with new data
                        panda_db.update_row(
                            workflow.id,
                            set_values + ' ' + where_clause,
                            fields
                        )

                # Insert the form in the context
                context['row_form'] = row_form

            else:
                if request.POST['submit'] == 'submit':
                    # Add error in form and redisplay
                    form.add_error(None, 'No data found with the given keys')
                else:
                    form.add_error(None, 'Modification not allowed')

    return render(request, 'dataops/row_filter.html', context)


@login_required
@user_passes_test(is_instructor)
def row_update(request):
    """
    Receives a POST request to update a row in the data matrix
    :param request: Request object with all the data.
    :return:
    """

    # This method can only be invoked through a POST operation
    if request.method == 'GET':
        return redirect('dataops:rowfilter')

    workflow = get_object_or_404(
        Workflow,
        pk=request.session.get('ontask_workflow_id', -1),
        user=request.user)

    # If the workflow has no data, something went wrong, go back to the
    # rowfilter page
    if workflow.nrows == 0:
        return redirect('dataops:rowfilter')

    # Initialise the form
    row_form = RowUpdateForm(request.POST,
                             workflow=workflow)

    # If the form was not valid, something went wrong
    if not row_form.is_valid():
        return redirect('dataops:rowfilter')

    # Create the query to update thd row
    querystring = []
    queryfields = []
    unique_names = json.loads(workflow.column_unique)
    unique_name = None
    unique_field = None
    for name, value in row_form.cleaned_data.items():
        querystring.append(name + ' = %s')
        queryfields.append(value)

        if not unique_name and name in unique_names:
            unique_name = name
            unique_field = value

    # If there is no unique key, something went wrong.
    if not unique_name:
        raise Exception('Unique key not found when updating row')

    query = 'SET ' + ', '.join(querystring) + \
            ' WHERE {0} = %s'.format(unique_name)
    queryfields.append(unique_field)

    panda_db.update_row(workflow.id, query, queryfields)

    return redirect('dataops:rowfilter')
