# -*- coding: utf-8 -*-

"""Views to import/export a workflow."""
from builtins import str
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from ontask import OnTaskServiceException, models
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.workflow import services
from ontask.workflow.forms import WorkflowExportRequestForm, WorkflowImportForm


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def export_list_ask(
    request: http.HttpRequest,
    wid,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Request the list of actions to export (without data).

    :param request: Http request
    :param wid: workflow id
    :param workflow: workflow being manipulated
    :return: Http response.
    """
    return export_ask(
        request,
        wid=wid,
        workflow=workflow,
        only_action_list=True)


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def export_ask(
    request: http.HttpRequest,
    wid,
    workflow: Optional[models.Workflow] = None,
    only_action_list: Optional[bool] = False,
) -> http.HttpResponse:
    """Request additional information for the export.

    :param request: Http request
    :param wid: workflow id
    :param workflow: workflow being manipulated
    :param only_action_list: Boolean denoting export actions only.
    :return: Http response.
    """
    form = WorkflowExportRequestForm(
        request.POST or None,
        actions=workflow.actions.all(),
        put_labels=True)

    if request.method == 'POST' and form.is_valid():
        to_include = []
        for idx, a_id in enumerate(
            workflow.actions.values_list('id', flat=True),
        ):
            if form.cleaned_data['select_%s' % idx]:
                to_include.append(str(a_id))

        if not to_include and only_action_list:
            return redirect(reverse('action:index'))

        return render(
            request,
            'workflow/export_done.html',
            {'include': ','.join(to_include),
             'wid': workflow.id,
             'only_action_list': only_action_list})

    context = {
        'form': form,
        'name': workflow.name,
        'wid': workflow.id,
        'nactions': workflow.actions.count(),
        'only_action_list': only_action_list}

    if not only_action_list:
        context['nrows'] = workflow.nrows
        context['ncols'] = workflow.ncols

    # GET request, simply render the form
    return render(request, 'workflow/export.html', context)


@user_passes_test(is_instructor)
@require_http_methods(['GET'])
@get_workflow(pf_related='actions')
def export(
    request: http.HttpRequest,
    page_data: Optional[str] = '',
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the view to export a workflow.

    This request receives a parameter include with a comma separated list.
    The first value is a 0/1 stating if the data has to be included. The
    remaining elements are the ids of the actions to include

    :param request:
    :param page_data: Comma separated list of integers: First one is include: 0
    (do not include) or 1 include data and conditions, followed by the ids of
    the actions to include
    :param workflow: workflow being manipulated
    :return: Response with the file download
    """
    try:
        action_ids = [
            int(a_idx) for a_idx in page_data.split(',') if a_idx]
    except ValueError:
        return redirect('home')

    return services.do_export_workflow(workflow, action_ids)


@user_passes_test(is_instructor)
def import_workflow(request: http.HttpRequest):
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
        try:
            services.do_import_workflow(
                request.user,
                form.cleaned_data['name'],
                request.FILES['wf_file'])
        except OnTaskServiceException as exc:
            exc.message_to_error(request)

        # Go back to the list of workflows
        return redirect('home')

    return render(request, 'workflow/import.html', {'form': form})
