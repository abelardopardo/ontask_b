# -*- coding: utf-8 -*-

"""Views to run and serve actions."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask.action.evaluate import (
    evaluate_row_action_out, get_action_evaluation_context, get_row_values,
)
from ontask.action.forms import ValueExcludeForm
from ontask.action.payloads import get_action_payload, set_action_payload
from ontask.action.views.run_canvas_email import run_canvas_email_action
from ontask.action.views.run_email import run_email_action
from ontask.action.views.run_json import run_json_action
from ontask.action.views.run_json_list import run_json_list_action
from ontask.action.views.run_send_list import run_send_list_action
from ontask.action.views.run_survey import run_survey_action
from ontask.action.views.serve_survey import serve_survey_row
from ontask.core.celery import celery_is_up
from ontask.core.decorators import get_action, get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Action, Log, Workflow

fn_distributor = {
    Action.PERSONALIZED_TEXT: run_email_action,
    Action.PERSONALIZED_CANVAS_EMAIL: run_canvas_email_action,
    Action.PERSONALIZED_JSON: run_json_action,
    Action.RUBRIC_TEXT: None,
    Action.SURVEY: run_survey_action,
    Action.SEND_LIST: run_send_list_action,
    Action.SEND_LIST_JSON: run_json_list_action,
}


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def run_action(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Run specific run action view depending on action type.

    If it is a Survey or todo, renders a table with all rows that
    satisfy the filter condition and includes a link to enter data for each
    of them.

    :param request: HttpRequest
    :param pk: Action id. It is assumed to be an action In
    :return: HttpResponse
    """
    if not celery_is_up():
        messages.error(
            request,
            _('Unable to execute actions due to a misconfiguration. '
              + 'Ask your system administrator to enable message queueing.'))
        return redirect(reverse('action:index'))

    if action.action_type not in fn_distributor:
        # Incorrect type of action.
        messages.error(
            request,
            _('Execution for this action is not allowed.'))
        return redirect(reverse('action:index'))

    return fn_distributor[action.action_type](request, workflow, action)


@csrf_exempt
@xframe_options_exempt
@login_required
def serve_action_lti(request: HttpRequest) -> HttpResponse:
    """Serve an action accessed through LTI."""
    try:
        action_id = int(request.GET.get('id'))
    except Exception:
        raise Http404()

    return serve_action(request, action_id)


@csrf_exempt
@xframe_options_exempt
@login_required
def serve_action(request: HttpRequest, action_id: int) -> HttpResponse:
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
    action = Action.objects.filter(pk=int(action_id)).prefetch_related(
        'conditions',
    ).first()
    if not action or (not action.serve_enabled) or (not action.is_active):
        raise Http404

    if user_attribute_name not in action.workflow.get_column_names():
        raise Http404

    try:
        if action.is_out:
            response = serve_action_out(
                request.user,
                action,
                user_attribute_name)
        else:
            response = serve_survey_row(request, action, user_attribute_name)
    except Exception:
        raise Http404()

    return response


def serve_action_out(
    user,
    action: Action,
    user_attribute_name: str,
):
    """Serve request for an action out.

    Function that given a user and an Action Out
    searches for the appropriate data in the table with the given
    attribute name equal to the user email and returns the HTTP response.
    :param user: User object making the request
    :param action: Action to execute (action out)
    :param user_attribute_name: Column to check for email
    :return:
    """
    # For the response
    payload = {'action': action.name, 'action_id': action.id}

    # User_instance has the record used for verification
    row_values = get_row_values(action, (user_attribute_name, user.email))

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(action, row_values)
    if context is None:
        payload['error'] = (
            _('Error when evaluating conditions for user {0}').format(
                user.email,
            )
        )
        # Log the event
        Log.objects.register(
            user,
            Log.ACTION_SERVED_EXECUTE,
            workflow=action.workflow,
            payload=payload)
        return HttpResponse(render_to_string(
            'action/action_unavailable.html',
            {}))

    # Evaluate the action content.
    action_content = evaluate_row_action_out(action, context)

    # If the action content is empty, forget about it
    response = action_content
    if action_content is None:
        response = render_to_string('action/action_unavailable.html', {})
        payload['error'] = _('Action not enabled for user {0}').format(
            user.email,
        )

    # Log the event
    Log.objects.register(
        user,
        Log.ACTION_SERVED_EXECUTE,
        workflow=action.workflow,
        payload=payload)

    # Respond the whole thing
    return HttpResponse(response)


@user_passes_test(is_instructor)
@get_workflow()
def run_action_item_filter(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Offer a select widget to tick items to exclude from selection.

    This is a generic Web function. It assumes that the session object has a
    dictionary with a field stating what objects need to be considered for
    selection. It creates the right web form and then updates in the session
    dictionary the result and proceeds to a URL given also as part of that
    dictionary.

    :param request: HTTP request (GET) with a session object and a dictionary
    with the right parameters. The selected values are stored in the field
    'exclude_values'.

    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_action_payload(request.session)
    if not action_info:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect item filter invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(id=action_info['action_id'])

    form = ValueExcludeForm(
        request.POST or None,
        action=action,
        column_name=action_info['item_column'],
        form_info=action_info)

    context = {
        'form': form,
        'action': action,
        'button_label': action_info['button_label'],
        'valuerange': range(action_info['valuerange']),
        'step': action_info['step'],
        'prev_step': action_info['prev_url']}

    # The post is correct
    if request.method == 'POST' and form.is_valid():
        # Updating the payload in the session
        set_action_payload(request.session, action_info)

        return redirect(action_info['post_url'])

    return render(request, 'action/item_filter.html', context)
