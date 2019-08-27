# -*- coding: utf-8 -*-

"""Views to run JSON actions."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ontask.action.forms import JSONListActionForm
from ontask.action.payloads import JSONListPayload, set_action_payload
from ontask.action.send import send_json_list
from ontask.models import Action, Log, Workflow
from ontask.tasks import run_task


def run_json_list_action(
    req: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send JSON objects.

    Form asking for token and export wf

    :param req: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = JSONListPayload({'action_id': action.id})

    # Create the form to ask for the email subject and other information
    form = JSONListActionForm(req.POST or None, action_info=action_info)

    if req.method == 'POST' and form.is_valid():
        # Log the event
        log_item = Log.objects.register(
            req.user,
            Log.SCHEDULE_JSON_EXECUTE,
            action.workflow,
            {'action': action.name,
             'action_id': action.id,
             'exported_workflow': action_info['export_wf'],
             'status': 'Preparing to execute',
             'target_url': action.target_url})

        # Update the last_execution_log
        action.last_executed_log = log_item
        action.save()

        # Send the objects
        run_task.delay(
            send_json_list,
            req.user.id,
            log_item.id,
            action_info.get_store())

        # Reset object to carry action info throughout dialogs
        set_action_payload(req.session)
        req.session.save()

        # Successful processing.
        return render(
            req,
            'action/action_done.html',
            {'log_id': log_item.id, 'download': action_info['export_wf']})

    # Render the form
    return render(
        req,
        'action/request_json_data.html',
        {'action': action,
         'num_msgs': action.get_rows_selected(),
         'form': form,
         'valuerange': range(2),
         'rows_all_false': action.get_row_all_false_count()})
