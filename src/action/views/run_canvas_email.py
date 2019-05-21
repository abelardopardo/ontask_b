# -*- coding: utf-8 -*-

"""Views to run the personalized canvas email action."""

from datetime import datetime, timedelta
from typing import Optional

import pytz
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from action.forms import CanvasEmailActionForm
from action.models import Action
from action.payloads import (
    CanvasEmailPayload, action_session_dictionary, get_action_info,
)
from logs.models import Log
from ontask.decorators import get_workflow
from ontask.permissions import is_instructor
from ontask.tasks import send_canvas_email_messages
from ontask_oauth.models import OnTaskOAuthUserTokens
from ontask_oauth.views import get_initial_token_step1, refresh_token
from workflow.models import Workflow


def run_canvas_email_action(
    req: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Request data to send JSON objects.

    Form asking for subject, item column (contains ids to select unique users),
    confirm items (add extra step to drop items), export workflow and
    target_rul (if needed).

    :param req: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_action_info(
        req.session,
        CanvasEmailPayload,
        initial_values={
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:email_done')
        }
    )

    # Create the form to ask for the email subject and other information
    form = CanvasEmailActionForm(
        req.POST or None,
        column_names=[
            col.name for col in workflow.columns.filter(is_key=True)],
        action=action,
        action_info=action_info)

    if req.method == 'POST' and form.is_valid():
        # Request is a POST and is valid

        if action_info['confirm_items']:
            # Create a dictionary in the session to carry over all the
            # information to execute the next pages
            action_info['button_label'] = ugettext('Send')
            action_info['valuerange'] = 2
            action_info['step'] = 2
            req.session[action_session_dictionary] = action_info.get_store()

            return redirect('action:item_filter')

        # Go straight to the token request step
        return canvas_get_or_set_oauth_token(
            req,
            action_info['target_url'])

    # Render the form
    return render(
        req,
        'action/request_canvas_email_data.html',
        {'action': action,
         'num_msgs': action.get_rows_selected(),
         'form': form,
         'valuerange': range(2),
         'rows_all_false': action.get_row_all_false_count()})


@user_passes_test(is_instructor)
def canvas_get_or_set_oauth_token(
    request: HttpRequest,
    oauth_instance_name: str,
) -> HttpResponse:
    """Check for OAuth token, if not present, request a new one.

    Function that checks if the user has a Canvas OAuth token. If there is a
    token, the function goes straight to send the messages. If not, the OAuth
    process starts.

    :param request: Request object to process

    :param oauth_instance_name: Locator for the OAuth instance in OnTask

    :return: Http response
    """
    # Get the information from the payload
    oauth_info = ontask_settings.CANVAS_INFO_DICT.get(oauth_instance_name)
    if not oauth_info:
        messages.error(
            request,
            _('Unable to obtain Canvas OAuth information'),
        )
        return redirect('action:index')

    # Check if we have the token
    token = OnTaskOAuthUserTokens.objects.filter(
        user=request.user,
        instance_name=oauth_instance_name,
    ).first()
    if not token:
        # There is no token, authentication has to take place for the first
        # time
        token = get_initial_token_step1(
            request,
            oauth_info,
            reverse('action:canvas_email_done'))

    # Check if the token is valid
    now = datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))
    dead = now > token.valid_until - timedelta(
        seconds=ontask_settings.CANVAS_TOKEN_EXPIRY_SLACK)
    if dead:
        try:
            refresh_token(token, oauth_info)
        except Exception as exc:
            # Something went wrong when refreshing the token
            messages.error(
                request,
                _('Error when invoking Canvas API: {0}.'.format(str(exc))),
            )
            return redirect('action:index')

    return redirect('action:canvas_email_done')


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def run_canvas_email_done(
    request: HttpRequest,
    action_info: Optional[CanvasEmailPayload] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create the log object, queue the operation request and render done.

    :param request: HTTP request (GET)
    :param action_info: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """
    # Get the payload from the session if not given
    action_info = get_action_info(
        request.session,
        CanvasEmailPayload,
        action_info=action_info)
    if action_info is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(
            request,
            _('Incorrect canvas email action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = workflow.actions.filter(pk=action_info['action_id']).first()
    if not action:
        return redirect('home')

    # Log the event
    log_item = Log.objects.register(
        request.user,
        Log.SCHEDULE_CANVAS_EMAIL_EXECUTE,
        action.workflow,
        {
            'action': action.name,
            'action_id': action.id,
            'from_email': request.user.email,
            'subject': action_info['subject'],
            'exclude_values': action_info['exclude_values'],
            'email_column': action_info['item_column'],
            'target_url': action_info['target_url'],
            'status': 'Preparing to execute',
        })

    # Update the last_execution_log
    action.last_executed_log = log_item
    action.save()

    # Send the emails!
    send_canvas_email_messages.delay(
        request.user.id,
        log_item.id,
        action_info.get_store())

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = None
    request.session.save()

    # Successful processing.
    return render(
        request,
        'action/action_done.html',
        {'log_id': log_item.id, 'download': action_info['export_wf']})
