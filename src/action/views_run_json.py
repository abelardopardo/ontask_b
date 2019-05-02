# -*- coding: utf-8 -*-

"""Views to run JSON actions."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from action.forms_run import JSONActionForm
from action.models import Action
from action.payloads import (
    JSONPayload, action_session_dictionary, get_action_payload,
    get_action_info,
)
from logs.models import Log
from ontask.permissions import is_instructor
from ontask.tasks import celery_is_up, send_json_objects
from workflow.models import Workflow
from workflow.ops import get_workflow


def run_json_action(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send JSON objects.

    Form asking for token, key_column and if an item confirmation step is
    needed

    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_action_info(request.session, JSONPayload)
    if not action_info:
        action_info = JSONPayload(
            action_id=action.id,
            prev_url=reverse('action:run', kwargs={'pk': action.id}),
            post_url=reverse('action:json_done'))
        request.session[action_session_dictionary] = action_info.get_store()
        request.session.save()

    # Verify that celery is running!
    if not celery_is_up():
        messages.error(
            request,
            _('Unable to send json objects due to a misconfiguration. '
              + 'Ask your system administrator to enable JSON queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = JSONActionForm(
        request.POST or None,
        column_names=[
            col.name for col in workflow.columns.filter(is_key=True)],
        action_info=action_info)

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        num_msgs = action.get_rows_selected()

        # Render the form
        return render(
            request,
            'action/request_json_data.html',
            {'action': action,
             'num_msgs': num_msgs,
             'form': form,
             'valuerange': range(2),
             'rows_all_false': action.get_row_all_false_count()})

    # Request is a POST and is valid

    if action_info['confirm_items']:
        # Add information to the session object to execute the next pages
        action_info['button_label'] = ugettext('Send')
        action_info['valuerange'] = 2
        action_info['step'] = 2
        request.session[action_session_dictionary] = action_info.get_store()

        return redirect('action:item_filter')

    # Go straight to the final step.
    return json_done(request, action_info)


@user_passes_test(is_instructor)
def json_done(
    request: HttpRequest,
    action_info: Optional[JSONPayload] = None,
) -> HttpResponse:
    """Create the log object, queue the operation request, render DONE page.

    :param request: HTTP request (GET)
    :param action_info: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    # Get the payload from the session if not given
    action_info = get_action_info(request.session, JSONPayload, action_info)
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
         'status': 'Preparing to execute',
         'target_url': action.target_url})

    # Send the objects
    send_json_objects.delay(
        request.user.id,
        log_item.id,
        action_info)

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = None
    request.session.save()

    # Successful processing.
    return render(request, 'action/action_done.html', {'log_id': log_item.id})
