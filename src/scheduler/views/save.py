# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""

import datetime

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils.translation import ugettext, ugettext_lazy as _

from action.payloads import action_session_dictionary
from scheduler.forms import EmailScheduleForm, JSONScheduleForm
from scheduler.models import ScheduledAction
from scheduler.views.crud import finish_scheduling


def save_email_schedule(request, action, schedule_item, op_payload):
    """Handle the creation and edition of email items.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return:
    """
    # Create the form to ask for the email subject and other information
    form = EmailScheduleForm(
        form_data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=action.workflow.columns.filter(is_key=True),
        confirm_items=op_payload.get('confirm_items', False))

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():

        # Save the schedule item object
        s_item = form.save(commit=False)

        # Assign additional fields and save
        s_item.user = request.user
        s_item.action = action
        s_item.status = ScheduledAction.STATUS_CREATING
        s_item.payload = {
            'subject': form.cleaned_data['subject'],
            'cc_email': [
                email for email in form.cleaned_data['cc_email'].split(',')
                if email],
            'bcc_email': [
                email for email in form.cleaned_data['bcc_email'].split(',')
                if email],
            'send_confirmation': form.cleaned_data['send_confirmation'],
            'track_read': form.cleaned_data['track_read'],
        }
        # Verify that that action does comply with the name uniqueness
        # property (only with respec to other actions)
        try:
            s_item.save()
        except IntegrityError:
            # There is an action with this name already
            form.add_error(
                'name',
                _('A scheduled execution of this action with this name '
                  + 'already exists'))
            return render(
                request,
                'scheduler/edit.html',
                {
                    'action': action,
                    'form': form,
                    'now': datetime.datetime.now(pytz.timezone(
                        settings.TIME_ZONE)),
                },
            )

        # Upload information to the op_payload
        op_payload['schedule_id'] = s_item.id
        op_payload['confirm_items'] = form.cleaned_data['confirm_items']

        if op_payload['confirm_items']:
            # Update information to carry to the filtering stage
            op_payload['exclude_values'] = s_item.exclude_values
            op_payload['item_column'] = s_item.item_column.name
            op_payload['button_label'] = ugettext('Schedule')
            request.session[action_session_dictionary] = op_payload

            return redirect('action:item_filter')

        # If there is not item_column, the exclude values should be empty.
        s_item.exclude_values = []
        s_item.save()

        # Go straight to the final step
        return finish_scheduling(request, s_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        },
    )


def save_canvas_email_schedule(
    request,
    action,
    schedule_item,
    op_payload,
):
    """Create and edit canvas email scheduled actions.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return:
    """
    return render(request, 'under_construction.html', {})


def save_json_schedule(request, action, schedule_item, op_payload):
    """Create and edit scheduled json actions.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return:
    """
    # Create the form to ask for the email subject and other information
    form = JSONScheduleForm(
        form_data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=action.workflow.columns.filter(is_key=True),
        confirm_items=op_payload.get('confirm_items', False))

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():

        # Save the schedule item object
        s_item = form.save(commit=False)

        # Assign additional fields and save
        s_item.user = request.user
        s_item.action = action
        s_item.status = ScheduledAction.STATUS_CREATING
        s_item.payload = {'token': form.cleaned_data['token']}
        s_item.save()

        # Upload information to the op_payload
        op_payload['schedule_id'] = s_item.id

        if s_item.item_column:
            # Create a dictionary in the session to carry over all the
            # information to execute the next steps
            op_payload['item_column'] = s_item.item_column.name
            op_payload['exclude_values'] = s_item.exclude_values
            op_payload['button_label'] = ugettext('Schedule')
            request.session[action_session_dictionary] = op_payload

            return redirect('action:item_filter')

        # If there is not item_column, the exclude values should be empty.
        s_item.exclude_values = []
        s_item.save()

        # Go straight to the final step
        return finish_scheduling(request, s_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        },
    )
