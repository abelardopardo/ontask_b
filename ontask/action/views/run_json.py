# -*- coding: utf-8 -*-

"""Views to run JSON actions."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask.action import forms
from ontask.action.payloads import (
    JSONPayload, get_or_set_action_info, set_action_payload,
)
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Action, Log, Workflow
from ontask.tasks import run


def run_json_action(
    req: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send JSON objects.

    Form asking for token, item_column and if an item confirmation step is
    needed

    :param req: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_or_set_action_info(
        req.session,
        JSONPayload,
        initial_values={
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:json_done')},
        action=action)

    # Create the form to ask for the email subject and other information
    form = forms.JSONActionRunForm(
        req.POST or None,
        columns=workflow.columns.filter(is_key=True),
        action=action,
        form_info=action_info)

    if req.method == 'POST' and form.is_valid():
        if action_info['confirm_items']:
            # Add information to the session object to execute the next pages
            action_info['button_label'] = ugettext('Send')
            action_info['valuerange'] = 2
            action_info['step'] = 2
            set_action_payload(req.session, action_info.get_store())

            return redirect('action:item_filter')

        # Go straight to the final step.
        return run_json_done(
            req,
            action_info=action_info,
            workflow=workflow)

    # Render the form
    return render(
        req,
        'action/request_json_data.html',
        {'action': action,
         'num_msgs': action.get_rows_selected(),
         'form': form,
         'valuerange': range(2),
         'rows_all_false': action.get_row_all_false_count()})


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def run_json_done(
    request: HttpRequest,
    action_info: Optional[JSONPayload] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create the log object, queue the operation request, render DONE page.

    :param request: HTTP request (GET)

    :param action_info: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.

    :return: HTTP response
    """
    # Get the payload from the session if not given
    action_info = get_or_set_action_info(
        request.session,
        JSONPayload,
        action_info=action_info)
    if action_info is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect JSON action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = workflow.actions.filter(pk=action_info['action_id']).first()
    if not action:
        return redirect('home')

    # Log the event
    log_item = action.log(
        request.user,
        Log.ACTION_RUN_JSON,
        exclude_values=action_info['exclude_values'],
        item_column=action_info['item_column'],
        exported_workflow=action_info['export_wf'])

    # Send the objects
    run.delay(request.user.id, log_item.id, action_info.get_store())

    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    # Successful processing.
    return render(
        request,
        'action/action_done.html',
        {'log_id': log_item.id, 'download': action_info['export_wf']})
