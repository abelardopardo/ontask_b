# -*- coding: utf-8 -*-

"""Functions to update and create a row in the dataframe."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX, get_workflow, is_instructor
from ontask.dataops import forms, services, sql


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'actions'])
def row_create(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Process POST request to create a new row in the data table.

    :param request: Request object with all the data.
    :param workflow: Workflow being processed.
    :return: Nothing. Effect done in the database.
    """
    # If the workflow has no data, the operation should not be allowed
    if workflow.nrows == 0:
        return redirect('dataops:uploadmerge')

    # Create the form
    form = forms.RowForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        row_values = [
            form.cleaned_data[(ONTASK_UPLOAD_FIELD_PREFIX + '%s') % idx]
            for idx in range(workflow.columns.count())]
        try:
            services.create_row(workflow, row_values)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                request,
                'dataops/row_create.html',
                {'workflow': workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        workflow.log(
            request.user,
            models.Log.WORKFLOW_DATA_ROW_CREATE,
            new_values=list(
                zip([col.name for col in workflow.columns.all()],
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
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Process POST request to update a row in the data table.

    :param request: Request object with all the data.
    :param workflow: Workflow being manipulated
    :return: Http Response with the page rendering.
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
    form = forms.RowForm(
        request.POST or None,
        workflow=workflow,
        initial_values=sql.get_row(
            workflow.get_data_frame_table_name(),
            key_name=update_key,
            key_value=update_val,
            column_names=workflow.get_column_names()))

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return redirect('table:display')

        try:
            row_values = [
                form.cleaned_data[(ONTASK_UPLOAD_FIELD_PREFIX + '%s') % idx]
                for idx in range(workflow.columns.count())]
            services.update_row_values(
                workflow,
                update_key,
                update_val,
                row_values)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                request,
                'dataops/row_filter.html',
                {'workflow': workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        workflow.log(
            request.user,
            models.Log.WORKFLOW_DATA_ROW_UPDATE,
            new_values=list(zip(
                [col.name for col in workflow.columns.all()],
                [str(rval) for rval in row_values])))
        return redirect('table:display')

    return render(
        request,
        'dataops/row_filter.html',
        {'workflow': workflow,
         'form': form,
         'cancel_url': reverse('table:display')})
