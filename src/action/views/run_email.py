# -*- coding: utf-8 -*-

"""Views to run the email actions."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from action.forms import EmailActionForm
from action.models import Action
from action.payloads import (
    EmailPayload, action_session_dictionary, get_action_info,
)
from logs.models import Log
from ontask.permissions import is_instructor
from ontask.tasks import celery_is_up, send_email_messages
from workflow.models import Workflow
from workflow.ops import get_workflow

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


def run_email_action(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send emails.

    Form asking for subject line, email column, etc.
    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action being run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_action_info(request.session, EmailPayload)
    if not action_info:
        action_info = EmailPayload(
            action_id=action.id,
            prev_url=reverse('action:run', kwargs={'pk': action.id}),
            post_url=reverse('action:email_done'))
        request.session[action_session_dictionary] = action_info.get_store()
        request.session.save()

    if not celery_is_up():
        messages.error(
            request,
            _('Unable to send emails due to a misconfiguration. '
              + 'Ask your system administrator to enable email queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = EmailActionForm(
        request.POST or None,
        column_names=[
            col.name for col in workflow.columns.filter(is_key=True)],
        action=action,
        action_info=action_info)

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        num_msgs = action.get_rows_selected()

        # Render the form
        return render(
            request,
            'action/request_email_data.html',
            {'action': action,
             'num_msgs': num_msgs,
             'form': form,
             'valuerange': range(2)})

    # Request is a POST and is valid

    if action_info['confirm_items']:
        # Add information to the session object to execute the next pages
        action_info['button_label'] = ugettext('Send')
        action_info['valuerange'] = 2
        action_info['step'] = 2
        request.session[action_session_dictionary] = action_info.get_store()

        return redirect('action:item_filter')

    # Go straight to the final step.
    return run_email_done(request, action_info)


@user_passes_test(is_instructor)
def run_email_done(
    request: HttpRequest,
    action_info: Optional[EmailPayload] = None,
) -> HttpResponse:
    """Create the log object, queue the operation request and render done.

    :param request: HTTP request (GET)
    :param action_info: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    # Get the payload from the session if not given
    action_info = get_action_info(request.session, EmailPayload, action_info)
    if action_info is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect email action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = workflow.actions.filter(pk=action_info['action_id']).first()
    if not action:
        return redirect('home')

    # Log the event
    log_item = Log.objects.register(
        request.user,
        Log.SCHEDULE_EMAIL_EXECUTE,
        action.workflow,
        {
            'action': action.name,
            'action_id': action.id,
            'from_email': request.user.email,
            'subject': action_info['subject'],
            'cc_email': action_info['cc_email'],
            'bcc_email': action_info['bcc_email'],
            'send_confirmation': action_info['send_confirmation'],
            'track_read': action_info['track_read'],
            'exported_workflow': action_info['export_wf'],
            'exclude_values': action_info['exclude_values'],
            'email_column': action_info['item_column'],
            'status': 'Preparing to execute',
        })

    # Send the emails!
    send_email_messages.delay(
        request.user.id,
        log_item.id,
        action_info)

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = None
    request.session.save()

    # Successful processing.
    return render(
        request,
        'action/action_done.html',
        {'log_id': log_item.id, 'download': action_info['export_wf']})
