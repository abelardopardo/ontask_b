# -*- coding: utf-8 -*-

"""Views to run the send list actions."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ontask.action.forms import SendListActionForm
from ontask.action.payloads import SendListPayload
from ontask.action.send import send_list_email
from ontask.models import Action, Log, Workflow
from ontask.tasks import run_task

html_body = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>title</title>
  </head>
  <body>
    {0}
  </body>
</html>"""


def run_send_list_action(
    req: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send a list.

    Form asking for subject line and target email.

    :param req: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action being run
    :return: HTTP response
    """
    # Create the payload object with the required information
    action_info = SendListPayload({'action_id': action.id})

    # Create the form to ask for the email subject and other information
    form = SendListActionForm(
        req.POST or None,
        action=action,
        form_info=action_info)

    # Request is a POST and is valid
    if req.method == 'POST' and form.is_valid():
        # Log the event
        log_item = Log.objects.register(
            req.user,
            Log.SCHEDULE_EMAIL_EXECUTE,
            action.workflow,
            {
                'action': action.name,
                'action_id': action.id,
                'from_email': req.user.email,
                'recipient_email': action_info['email_to'] ,
                'subject': action_info['subject'],
                'cc_email': action_info['cc_email'],
                'bcc_email': action_info['bcc_email'],
                'status': 'Preparing to execute',
            })

        # Update the last_execution_log
        action.last_executed_log = log_item
        action.save()

        # Send the emails!
        run_task.delay( req.user.id, log_item.id, action_info.get_store())

        # Successful processing.
        return render(
            req,
            'action/action_done.html',
            {'log_id': log_item.id, 'download': action_info['export_wf']})

    # Render the form
    return render(
        req,
        'action/request_send_list_data.html',
        {'action': action,
         'form': form,
         'valuerange': range(2)})
