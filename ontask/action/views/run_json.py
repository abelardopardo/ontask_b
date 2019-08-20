# -*- coding: utf-8 -*-

"""Views to run JSON actions."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask.action.forms import JSONActionForm
from ontask.action.models import Action
from ontask.action.payloads import (
    JSONPayload, get_or_set_action_info, set_action_payload,
)
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Log
from ontask.tasks import send_json_objects
from ontask.workflow.models import Workflow


def run_json_action(
    req: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send JSON objects.

    Form asking for token, key_column and if an item confirmation step is
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
            'post_url': reverse('action:json_done')
        },
    )

    # Create the form to ask for the email subject and other information
    form = JSONActionForm(
        req.POST or None,
        column_names=[
            col.name for col in workflow.columns.filter(is_key=True)],
        action_info=action_info)

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
    log_item = Log.objects.register(
        request.user,
        Log.SCHEDULE_JSON_EXECUTE,
        action.workflow,
        {'action': action.name,
         'action_id': action.id,
         'exclude_values': action_info['exclude_values'],
         'key_column': action_info['item_column'],
         'exported_workflow': action_info['export_wf'],
         'status': 'Preparing to execute',
         'target_url': action.target_url})

    # Update the last_execution_log
    action.last_executed_log = log_item
    action.save()

    # Send the objects
    send_json_objects.delay(
        request.user.id,
        log_item.id,
        action_info.get_store())

    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    # Successful processing.
    return render(
        request,
        'action/action_done.html',
        {'log_id': log_item.id, 'download': action_info['export_wf']})
