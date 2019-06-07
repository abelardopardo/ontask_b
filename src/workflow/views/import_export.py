# -*- coding: utf-8 -*-

"""Functions to import/export a workflow."""

from builtins import str
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ontask.decorators import get_workflow
from ontask.permissions import is_instructor
from workflow.forms import WorkflowExportRequestForm, WorkflowImportForm
from workflow.import_export import do_export_workflow, do_import_workflow
from workflow.models import Workflow


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def export_ask(
    request: HttpRequest,
    wid,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Request additional information for the export."""
    form = WorkflowExportRequestForm(
        request.POST or None,
        actions=workflow.actions.all(),
        put_labels=True)

    context = {
        'form': form,
        'name': workflow.name,
        'nrows': workflow.nrows,
        'ncols': workflow.ncols,
        'nactions': workflow.actions.count(),
        'wid': workflow.id,
    }

    if request.method == 'POST' and form.is_valid():
        to_include = []
        for idx, a_id in enumerate(
            workflow.actions.all().values_list('id', flat=True),
        ):
            if form.cleaned_data['select_%s' % idx]:
                to_include.append(str(a_id))
        return render(
            request,
            'workflow/export_done.html',
            {'include': ','.join(to_include),
             'wid': workflow.id})

    # GET request, simply render the form
    return render(request, 'workflow/export.html', context)


@user_passes_test(is_instructor)
@require_http_methods(['GET'])
@get_workflow(pf_related='actions')
def export(
    request: HttpRequest,
    page_data,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the view to export a workflow.

    This request receives a parameter include with a comma separated list.
    The first value is a 0/1 stating if the data has to be included. The
    remaining elements are the ids of the actions to include

    :param request:

    :param page_data: Comma separated list of integers: First one is include: 0
    (do not include) or 1 include data and conditions, followed by the ids of
    the actions to include

    :return:
    """
    # Get the param encoding which elements to include in the export.
    if page_data == '0':
        action_ids = [action.id for action in workflow.actions.all()]
    else:
        # Data has at least one integer
        try:
            action_ids = [int(a_idx) for a_idx in page_data.split(',')]
        except ValueError:
            return redirect('home')

    response = do_export_workflow(workflow, action_ids)

    return response


@user_passes_test(is_instructor)
def import_workflow(request):
    """View to handle the workflow import.

    View that handles a form for workflow import. It receives a file that
    needs to be unpacked and the data uploaded. In this method there are some
    basic checks to verify that the import procedure can go ahead.

    :param request: HTTP request

    :return: Rendering of the import page or back to the workflow index
    """
    form = WorkflowImportForm(
        request.POST or None,
        request.FILES or None,
        user=request.user)

    if request.method == 'POST' and form.is_valid():
        # UPLOAD THE FILE!
        status = do_import_workflow(
            request.user,
            form.cleaned_data['name'],
            request.FILES['wf_file'])

        # If something went wrong, show at to the top of the page
        if status:
            messages.error(request, status)

        # Go back to the list of workflows
        return redirect('home')

    return render(request, 'workflow/import.html', {'form': form})
