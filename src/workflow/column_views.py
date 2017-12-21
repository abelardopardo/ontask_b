# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse

import logs.ops
from action.models import Condition
from dataops import ops, formula_evaluation, pandas_db
from ontask.permissions import is_instructor
from .forms import (ColumnRenameForm,
                    ColumnAddForm)
from .models import Column
from .ops import get_workflow, workflow_delete_column, clone_column


@user_passes_test(is_instructor)
def column_add(request):
    # Data to send as JSON response
    data = {}

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    if workflow.nrows == 0:
        data['form_is_valid'] = True
        data['html_redirect'] = ''
        messages.error(
            request,
            'Cannot add column to a workflow without data')
        return JsonResponse(data)

    # Form to read/process data
    form = ColumnAddForm(request.POST or None, workflow=workflow)

    # If a GET or incorrect request, render the form again
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(
            'workflow/includes/partial_column_add.html',
            {'form': form},
            request=request)

        return JsonResponse(data)

    # Processing now a valid POST request
    # Access the updated information
    column_initial_value = form.initial_valid_value

    # Save the column object attached to the form
    column = form.save(commit=False)

    # Fill in the remaining fields in the column
    column.workflow = workflow
    column.is_key = False
    column.save()

    # Update the data frame, which must be stored in the form because
    # it was loaded when validating it.
    df = pandas_db.load_from_db(workflow.id)

    # Add the column with the initial value
    df = ops.data_frame_add_empty_column(df,
                                         column.name,
                                         column.data_type,
                                         column_initial_value)
    # Store the df to DB
    ops.store_dataframe_in_db(df, workflow.id)

    # Log the event
    logs.ops.put(request.user,
                 'column_add',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'column_name': column.name,
                  'column_type': column.data_type})

    data['form_is_valid'] = True
    data['html_redirect'] = reverse('workflow:detail',
                                    kwargs={'pk': workflow.id})
    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_edit(request, pk):
    # Data to send as JSON response
    data = {}

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Get the column object and make sure it belongs to the workflow
    try:
        column = Column.objects.get(pk=pk,
                                    workflow=workflow)
    except ObjectDoesNotExist:
        # Something went wrong, redirect to the workflow detail page
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Form to read/process data
    form = ColumnRenameForm(request.POST or None,
                            workflow=workflow,
                            instance=column)

    old_name = column.name
    context = {'form': form,
               'cname': old_name,
               'pk': pk}

    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(
            'workflow/includes/partial_column_edit.html',
            context,
            request=request)

        return JsonResponse(data)

    # Processing a POST request with valid data in the form

    # Process further only if any data changed.
    if form.changed_data:
        # Some field changed value, so save the result, but
        # no commit as we need to propagate the info to the df
        column = form.save(commit=False)

        # Get the data frame from the form (should be
        # loaded)
        df = form.data_frame

        # If there is a new name, rename the data frame columns
        if 'name' in form.changed_data:
            # Rename the column in the data frame
            df = ops.rename_df_column(df,
                                      workflow,
                                      old_name,
                                      column.name)

        # Save the column information
        form.save()

        # Changes in column require rebuilding the query_builder_ops
        workflow.set_query_builder_ops()

        # Save the workflow
        workflow.save()

        # And save the DF in the DB
        ops.store_dataframe_in_db(df, workflow.id)

    data['form_is_valid'] = True
    data['html_redirect'] = ''

    # Log the event
    logs.ops.put(request.user,
                 'column_rename',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'column_name': old_name,
                  'new_name': column.name})

    # Done processing the correct POST request
    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_delete(request, pk):
    """
    Delete a column in the table attached to a workflow
    :param request: HTTP request
    :param pk: ID of the column to delete. The workflow element is taken
     from the session.
    :return: Render the delete column form
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The column is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    unique_column = workflow.get_column_unique()
    if column.is_key and len([x for x in unique_column if x]) == 1:
        # This is the only key column
        messages.error(request, 'You cannot delete the only key column')
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the column to delete
    context['cname'] = column.name

    # Get the conditions/actions attached to this workflow
    cond_to_delete = [x for x in Condition.objects.filter(
        action__workflow=workflow)
                      if formula_evaluation.has_variable(x.formula,
                                                         column.name)]
    # Put it in the context because it is shown to the user before confirming
    # the deletion
    context['cond_to_delete'] = cond_to_delete

    if request.method == 'POST':
        # Proceed deleting the column
        workflow_delete_column(workflow, column, cond_to_delete)

        # Log the event
        logs.ops.put(request.user,
                     'column_delete',
                     workflow,
                     {'id': workflow.id,
                      'name': workflow.name,
                      'column_name': column.name})

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'workflow/includes/partial_column_delete.html',
        context,
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_clone(request, pk):
    """
    Clone a column in the table attached to a workflow
    :param request: HTTP request
    :param pk: ID of the column to clone. The workflow element is taken
     from the session.
    :return: Render the clone column form
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The column is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the column to clone
    context['cname'] = column.name

    if request.method == 'GET':
        data['html_form'] = render_to_string(
            'workflow/includes/partial_column_clone.html',
            context,
            request=request)

        return JsonResponse(data)

    # POST REQUEST

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy_of_' + column.name
    while Column.objects.filter(name=new_name,
                                workflow=column.workflow).exists():
        new_name = 'Copy_of_' + new_name

    # Proceed to clone the column
    column = clone_column(column, None, new_name)

    # Log the event
    logs.ops.put(request.user,
                 'column_clone',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'new_column_name': column.name})

    data['form_is_valid'] = True
    data['html_redirect'] = reverse('workflow:detail',
                                    kwargs={'pk': workflow.id})

    return JsonResponse(data)
