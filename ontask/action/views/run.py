# -*- coding: utf-8 -*-

"""Views to run and serve actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import models
from ontask.action import forms, services
from ontask.core import DataTablesServerSidePaging, SessionPayload
from ontask.core import celery_is_up
from ontask.core.decorators import ajax_required, get_action, get_workflow
from ontask.core.permissions import is_instructor


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def run_action(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.HttpResponse:
    """Run specific run action view depending on action type.

    If it is a Survey or todo, renders a table with all rows that
    satisfy the filter condition and includes a link to enter data for each
    of them.

    :param request: HttpRequest
    :param pk: Action id. It is assumed to be an action In
    :param workflow: Workflow object to be assigned by the decorators
    :param action: Action object to be assigned by the decorators
    :return: HttpResponse
    """
    if not celery_is_up():
        messages.error(
            request,
            _('Unable to execute actions due to a misconfiguration. '
              + 'Ask your system administrator to enable message queueing.'))
        return redirect(reverse('action:index'))

    return services.action_process_factory.process_run_request(
        action.action_type,
        request=request,
        action=action,
        prev_url=reverse('action:run', kwargs={'pk': action.id}))


@user_passes_test(is_instructor)
@get_workflow()
def run_done(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Finish the create/edit operation of a scheduled operation."""
    payload = SessionPayload(request.session)
    if payload is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(
            request,
            _('Incorrect action run invocation.'))
        return redirect('action:index')

    return services.action_process_factory.process_run_request_done(
        payload.get('operation_type'),
        request=request,
        workflow=workflow,
        payload=payload)


@user_passes_test(is_instructor)
@get_action()
def zip_action(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.HttpResponse:
    """Request data to create a zip file.

    Form asking for participant column, user file name column, file suffix,
    if it is a ZIP for Moodle and confirm users step.

    :param req: HTTP request (GET)
    :param pk: Action key
    :return: HTTP response
    """
    del workflow, pk
    return services.action_process_factory.process_run_request(
        models.action.ZIP_OPERATION,
        request=request,
        action=action,
        prev_url=reverse('action:zip_action', kwargs={'pk': action.id}))


@csrf_exempt
@xframe_options_exempt
@login_required
def serve_action_lti(request: http.HttpRequest) -> http.HttpResponse:
    """Serve an action accessed through LTI."""
    try:
        action_id = int(request.GET.get('id'))
    except Exception:
        raise http.Http404()

    return serve_action(request, action_id)


@csrf_exempt
@xframe_options_exempt
@login_required
def serve_action(
    request: http.HttpRequest,
    action_id: int,
) -> http.HttpResponse:
    """Serve the rendering of an action in a workflow for a given user.

    - uatn: User attribute name. The attribute to check for authentication.
      By default this will be "email".

    - uatv: User attribute value. The value to check with respect to the
      previous attribute. The default is the user attached to the request.

    If the two last parameters are given, the authentication is done as:

    user_record[user_attribute_name] == user_attribute_value

    :param request: Http Request
    :param action_id: Action ID to use
    :return: Http response
    """
    # Get the parameters
    user_attribute_name = request.GET.get('uatn', 'email')

    # Get the action object
    action = models.Action.objects.filter(pk=int(action_id)).prefetch_related(
        'conditions',
    ).first()
    if not action or (not action.serve_enabled) or (not action.is_active):
        raise http.Http404

    if user_attribute_name not in action.workflow.get_column_names():
        raise http.Http404

    try:
        if action.is_out:
            response = services.serve_action_out(
                request.user,
                action,
                user_attribute_name)
        else:
            response = services.serve_survey_row(
                request,
                action,
                user_attribute_name)
    except Exception:
        raise http.Http404()

    return response


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def run_action_item_filter(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Offer a select widget to tick items to exclude from selection.

    This is a generic Web function. It assumes that the session object has a
    dictionary with a field stating what objects need to be considered for
    selection. It creates the right web form and then updates in the session
    dictionary the result and proceeds to a URL given also as part of that
    dictionary.

    :param request: HTTP request (GET) with a session object and a dictionary
    with the right parameters. The selected values are stored in the field
    'exclude_values'.

    :param: workflow: Workflow object being processed.

    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    payload = SessionPayload(request.session)
    if payload is None:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect item filter invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    try:
        action = workflow.actions.get(pk=payload['action_id'])
        item_column = workflow.columns.get(pk=payload['item_column'])
    except Exception:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect item filter invocation.'))
        return redirect('action:index')

    form = forms.ValueExcludeForm(
        request.POST or None,
        action=action,
        column_name=item_column.name,
        form_info=payload)

    context = {
        'form': form,
        'action': action,
        'button_label': payload['button_label'],
        'valuerange': range(payload['valuerange']),
        'step': payload['step'],
        'prev_step': payload['prev_url']}

    # The post is correct
    if request.method == 'POST' and form.is_valid():
        # Updating the payload in the session
        return redirect(payload['post_url'])

    return render(request, 'action/item_filter.html', context)


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_zip_export(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Create a zip with the personalised text and return it as response.

    :param request: Request object with a Dictionary with all the required
    information
    :return: Response (download)
    """
    # Get the payload from the session if not given
    payload = SessionPayload(request.session)
    if not payload:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect ZIP action invocation.'))
        return redirect('action:index')

    # Payload has the right keys
    if any(
        key_name not in payload.keys()
        for key_name in [
            'action_id', 'zip_for_moodle', 'item_column', 'user_fname_column',
            'file_suffix']):
        messages.error(
            request,
            _('Incorrect payload in ZIP action invocation'))
        return redirect('action:index')

    # Get the action
    action = workflow.actions.filter(pk=payload['action_id']).first()
    if not action:
        return redirect('home')

    item_column = workflow.columns.get(pk=payload['item_column'])
    if not item_column:
        messages.error(
            request,
            _('Incorrect payload in ZIP action invocation'))
        return redirect('action:index')

    user_fname_column = None
    if payload['user_fname_column']:
        user_fname_column = workflow.columns.get(
            pk=payload['user_fname_column'])

    # Create the ZIP with the eval data tuples and return it for download
    return services.create_and_send_zip(
        request.session,
        action,
        item_column,
        user_fname_column,
        payload)


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_action(pf_related='actions')
def show_survey_table_ss(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Show elements in table that satisfy filter request.

    Serve the AJAX requests to show the elements in the table that satisfy
    the filter and between the given limits.
    :param request:
    :param pk: action id being run
    :return:
    """
    # Check that the GET parameters are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return http.JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    return services.create_survey_table(workflow, action, dt_page)


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def run_survey_row(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.HttpResponse:
    """Render form for introducing information in a single row.

    Function that runs the action in for a single row. The request
    must have query parameters uatn = key name and uatv = key value to
    perform the lookup.

    :param request:

    :param pk: Action id. It is assumed to be an action In

    :return:
    """
    # If the action is an "out" action, return to index
    if action.is_out:
        return redirect('action:index')

    # Get the parameters
    user_attribute_name = request.GET.get('uatn', 'email')

    return services.serve_survey_row(request, action, user_attribute_name)


@login_required
def survey_thanks(request: http.HttpRequest) -> http.HttpResponse:
    """Respond simply saying thanks.

    :param request: Http requst
    :return: Http response
    """
    return render(request, 'thanks.html', {})
