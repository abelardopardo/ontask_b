# -*- coding: utf-8 -*-

"""Views for import/export."""

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from action.forms import ActionImportForm
from action.import_export import do_export_action, do_import_action
from ontask.permissions import is_instructor
from workflow.ops import get_workflow


@user_passes_test(is_instructor)
def export_ask(request: HttpRequest, pk: int) -> HttpResponse:
    """Ask for confirmation before exporting an action.

    :param request: HTTP request
    :param pk: Action ID
    :return: HTTP response to the next page where the export is done
    """
    # Get the workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    action = workflow.actions.filter(pk=pk).prefetch_related(
        'column_condition_pair',
    ).first()
    if not action:
        return redirect('action:index')

    # GET request, simply render the form
    return render(
        request,
        'action/export_ask.html',
        {'action': action,
         'cnames': [
             cpair.column.name
             for cpair in action.column_condition_pair.all()]})


@user_passes_test(is_instructor)
def export_done(request: HttpRequest, pk: int) -> HttpResponse:
    """Show page stating that export operation has finished.

    :param request:
    :param pk: Unique key of the action to export
    :return: HTTP response
    """
    # Get the workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    action = workflow.actions.filter(pk=pk).first()
    if not action:
        return redirect('action:index')

    return render(request, 'action/export_done.html', {'action': action})


@user_passes_test(is_instructor)
def export_download(request: HttpRequest, pk: int) -> HttpResponse:
    """Export the action pointed by the pk.

    :param request:
    :param pk: Unique key of the action to export
    :return: HTTP response
    """
    # Get the workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    action = workflow.actions.filter(pk=pk).first()
    if not action:
        return redirect('action:index')

    response = do_export_action(action)

    return response


@user_passes_test(is_instructor)
def action_import(request: HttpRequest) -> HttpResponse:
    """Import one action given in a gz file.

    :param request: Http request
    :return: HTTP response
    """
    # Get workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    form = ActionImportForm(
        request.POST or None,
        request.FILES or None,
        workflow=workflow,
        user=request.user)

    context = {'form': form}

    # If a get request or the form is not valid, render the page.
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/import.html', context)

    # Process the reception of the file
    if not form.is_multipart():
        form.add_error(
            None,
            _('Incorrect form request (it is not multipart)'))
        return render(request, 'action/import.html', context)

    # UPLOAD THE FILE!
    try:
        do_import_action(
            request.user,
            workflow,
            form.cleaned_data['name'],
            request.FILES['upload_file'])
    except Exception as exc:
        # Attach the exception to the request
        messages.error(
            request,
            _('Unable to import action: {0}').format(exc),
        )

    # Go back to the list of actions
    return redirect('action:index')
