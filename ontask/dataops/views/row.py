# -*- coding: utf-8 -*-

"""Functions to update and create a row in the dataframe."""

from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.forms import FIELD_PREFIX, RowForm
from ontask.dataops.sql import get_row, update_row
from ontask.dataops.sql.row_queries import insert_row
from ontask.models import Log, Workflow
from ontask.workflow.ops import check_key_columns


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'actions'])
def row_create(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Process POST request to create a new row in the data table.

    :param request: Request object with all the data.

    :return: Nothing. Effect done in the database.
    """
    # If the workflow has no data, the operation should not be allowed
    if workflow.nrows == 0:
        return redirect('dataops:uploadmerge')

    # Create the form
    form = RowForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Create the query to update the row
        columns = workflow.columns.all()
        column_names = [col.name for col in columns]
        row_values = [
            form.cleaned_data[(FIELD_PREFIX + '%s') % idx]
            for idx in range(len(columns))]

        try:
            with transaction.atomic():
                # Insert the new row in the db
                insert_row(
                    workflow.get_data_frame_table_name(),
                    column_names,
                    row_values)
                # verify that the "key" property is maintained in all the
                # columns.
                check_key_columns(workflow)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                request,
                'dataops/row_create.html',
                {'workflow': workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        # Update number of rows
        workflow.nrows += 1
        workflow.save()

        # Recompute all the values of the conditions in each of the actions
        # TODO: Explore how to do this asynchronously (or lazy)
        map(lambda act: act.update_n_rows_selected(), workflow.actions.all())
        workflow.log(
            request.user,
            Log.WORKFLOW_DATA_ROW_CREATE,
            new_values=list(
                zip(column_names,
                    [str(rval) for rval in row_values])))
        return redirect('table:display')

    return render(
        request,
        'dataops/row_create.html',
        {'workflow': workflow,
         'form': form,
         'cancel_url': reverse('table:display')})


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def row_update(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Process POST request to update a row in the data table.

    :param request: Request object with all the data.

    :return:
    """
    # Get the pair key,value to fetch the row from the table
    update_key = request.GET.get('k')
    update_val = request.GET.get('v')

    if not update_key or not update_val:
        # Malformed request
        return render(
            request,
            'error.html',
            {'message': _('Unable to update table row')})

    # Get the form populated with the row values
    form = RowForm(
        request.POST or None,
        workflow=workflow,
        initial_values=get_row(
            workflow.get_data_frame_table_name(),
            key_name=update_key,
            key_value=update_val,
            column_names=workflow.get_column_names()))

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return redirect('table:display')

        # Create the query to update the row
        column_names = [col.name for col in workflow.columns.all()]
        row_values = [
            form.cleaned_data[(FIELD_PREFIX + '%s') % idx]
            for idx in range(len(column_names))]

        try:
            with transaction.atomic():
                # Update the row in the db
                update_row(
                    workflow.get_data_frame_table_name(),
                    column_names,
                    row_values,
                    filter_dict={update_key: update_val})
                # verify that the "key" property is maintained in all the
                # columns.
                check_key_columns(workflow)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                request,
                'dataops/row_filter.html',
                {'workflow': workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        # Recompute all the values of the conditions in each of the actions
        # TODO: Explore how to do this asynchronously (or lazy)
        for act in workflow.actions.all():
            act.update_n_rows_selected()
        workflow.log(
            request.user,
            Log.WORKFLOW_DATA_ROW_UPDATE,
            new_values=list(zip(
                column_names,
                [str(rval) for rval in row_values])))
        return redirect('table:display')

    return render(
        request,
        'dataops/row_filter.html',
        {'workflow': workflow,
         'form': form,
         'cancel_url': reverse('table:display')})
