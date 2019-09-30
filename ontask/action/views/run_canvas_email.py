# -*- coding: utf-8 -*-

"""Views to run the personalized canvas email action."""

from datetime import datetime, timedelta
from typing import Optional

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask.action.forms import CanvasEmailActionForm
from ontask.action.payloads import (
    CanvasEmailPayload, get_or_set_action_info, set_action_payload,
)
from ontask.action.send import send_canvas_emails
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Action, Log, OAuthUserToken, Workflow
from ontask.oauth.views import get_initial_token_step1, refresh_token
from ontask.tasks import run_task


def run_canvas_email_action(
    req: WSGIRequest,
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
    action_info = get_or_set_action_info(
        req.session,
        CanvasEmailPayload,
        initial_values={
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:canvas_email_done'),
        },
    )

    # Create the form to ask for the email subject and other information
    form = CanvasEmailActionForm(
        req.POST or None,
        column_names=[
            col.name for col in workflow.columns.filter(is_key=True)],
        action=action,
        form_info=action_info)

    if req.method == 'POST' and form.is_valid():
        # Request is a POST and is valid

        if action_info['confirm_items']:
            # Create a dictionary in the session to carry over all the
            # information to execute the next pages
            action_info['button_label'] = ugettext('Send')
            action_info['valuerange'] = 2
            action_info['step'] = 2
            set_action_payload(req.session, action_info.get_store())
            continue_url = 'action:item_filter'
        else:
            continue_url = 'action:canvas_email_done'

        # Check for the CANVAS token and proceed to the continue_url
        return canvas_get_or_set_oauth_token(
            req,
            action_info['target_url'],
            continue_url)

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
    request: WSGIRequest,
    oauth_instance_name: str,
    continue_url: str,
) -> HttpResponse:
    """Check for OAuth token, if not present, request a new one.

    Function that checks if the user has a Canvas OAuth token. If there is a
    token, the function goes straight to send the messages. If not, the OAuth
    process starts.

    :param request: Request object to process

    :param oauth_instance_name: Locator for the OAuth instance in OnTask

    :param continue_url: URL to continue if the token exists and is valid

    :return: Http response
    """
    # Get the information from the payload
    oauth_info = settings.CANVAS_INFO_DICT.get(oauth_instance_name)
    if not oauth_info:
        messages.error(
            request,
            _('Unable to obtain Canvas OAuth information'),
        )
        return redirect('action:index')

    # Check if we have the token
    token = OAuthUserToken.objects.filter(
        user=request.user,
        instance_name=oauth_instance_name,
    ).first()
    if not token:
        # There is no token, authentication has to take place for the first
        # time
        return get_initial_token_step1(
            request,
            oauth_info,
            reverse(continue_url))

    # Check if the token is valid
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    dead = now > token.valid_until - timedelta(
        seconds=settings.CANVAS_TOKEN_EXPIRY_SLACK)
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

    return redirect(continue_url)


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def run_canvas_email_done(
    request: WSGIRequest,
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
    action_info = get_or_set_action_info(
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
    log_item = action.log(
        request.user,
        Log.ACTION_RUN_CANVAS_EMAIL,
        action.workflow,
        **{
            'from_email': request.user.email,
            'subject': action_info['subject'],
            'exclude_values': action_info['exclude_values'],
            'item_column': action_info['item_column'],
            'target_url': action_info['target_url'],
            'status': 'Preparing to execute',
        })

    # Send the emails!
    run_task.delay(request.user.id, log_item.id, action_info.get_store())

    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    # Successful processing.
    return render(
        request,
        'action/action_done.html',
        {'log_id': log_item.id, 'download': action_info['export_wf']})
