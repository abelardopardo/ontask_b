# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""

import datetime
from typing import Dict

from django.http import HttpRequest, HttpResponse
import pytz
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask.action.payloads import (
    action_session_dictionary, set_action_payload,
)
from ontask.models import Action, Log, ScheduledAction
from ontask.scheduler.forms import (
    EmailScheduleForm, JSONScheduleForm, SendListScheduleForm,
    JSONListScheduleForm
)


def create_timedelta_string(dtime: datetime.datetime) -> str:
    """Create a string rendering a time delta between now and the given one.

    The rendering proceeds gradually to see if the words days, hours, minutes
    etc. are needed.

    :param dtime: datetime object

    :return: String rendering
    """
    tdelta = dtime - datetime.datetime.now(
        pytz.timezone(settings.TIME_ZONE))
    delta_string = []
    if tdelta.days // 365 >= 1:
        delta_string.append(ugettext('{0} years').format(tdelta.days // 365))
    days = tdelta.days % 365
    if days != 0:
        delta_string.append(ugettext('{0} days').format(days))
    hours = tdelta.seconds // 3600
    if hours != 0:
        delta_string.append(ugettext('{0} hours').format(hours))
    minutes = (tdelta.seconds % 3600) // 60
    if minutes != 0:
        delta_string.append(ugettext('{0} minutes').format(minutes))

    return ', '.join(delta_string)


def save_email_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict
) -> HttpResponse:
    """Handle the creation and edition of email items.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return: Http response with the rendered page
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
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            set_action_payload(request.session, op_payload)

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
            'valuerange': range(2),
        },
    )


def save_send_list_schedule(request, action, schedule_item, op_payload):
    """Handle the creation and edition of send list items.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return:
    """
    # Create the form to ask for the email subject and other information
    form = SendListScheduleForm(
        form_data=request.POST or None,
        action=action,
        instance=schedule_item)

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():

        # Save the schedule item object
        s_item = form.save(commit=False)

        # Assign additional fields and save
        s_item.user = request.user
        s_item.action = action
        s_item.status = ScheduledAction.STATUS_CREATING
        s_item.payload = {
            'email_to': form.cleaned_data['email_to'],
            'subject': form.cleaned_data['subject'],
            'cc_email': [
                email for email in form.cleaned_data['cc_email'].split(',')
                if email],
            'bcc_email': [
                email for email in form.cleaned_data['bcc_email'].split(',')
                if email]}

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
            'valuerange': range(2),
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


def save_json_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict
) -> HttpResponse:
    """Create and edit scheduled json actions.

    :param request: Http request being processed

    :param action: Action item related to the schedule

    :param schedule_item: Schedule item or None if it is new

    :param op_payload: dictionary to carry over the request to the next step

    :return: Http response with the rendered page
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
        op_payload['confirm_items'] = form.cleaned_data['confirm_items']

        if op_payload['confirm_items']:
            # Create a dictionary in the session to carry over all the
            # information to execute the next steps
            op_payload['item_column'] = s_item.item_column.name
            op_payload['exclude_values'] = s_item.exclude_values
            op_payload['button_label'] = ugettext('Schedule')
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            set_action_payload(request.session, op_payload)

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
            'valuerange': range(2),
        },
    )


def save_send_list_json_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict,
) -> HttpResponse:
    """Save a scheduled action of type json list.

    :param request: Http requested received
    :param action: Action object
    :param schedule_item: Scheduled item
    :param op_payload: Payload for the scheduled item.
    :return:
    """
    # Create the form to ask for the email subject and other information
    form = JSONListScheduleForm(
        form_data=request.POST or None,
        action=action,
        instance=schedule_item)

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
            'valuerange': range(2),
        },
    )


def finish_scheduling(request, schedule_item=None, payload=None):
    """Finalize the creation of a scheduled action.

    All required data is passed through the payload.

    :param request: Request object received

    :param schedule_item: ScheduledAction item being processed. If None,
    it has to be extracted from the information in the payload.

    :param payload: Dictionary with all the required data coming from
    previous requests.

    :return:
    """
    # Get the payload from the session if not given
    if payload is None:
        payload = request.session.get(action_session_dictionary)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(
                request,
                _('Incorrect action scheduling invocation.'))
            return redirect('action:index')

    # Get the scheduled item if needed
    if not schedule_item:
        s_item_id = payload.get('schedule_id')
        if not s_item_id:
            messages.error(
                request,
                _('Incorrect parameters in action scheduling'))
            return redirect('action:index')

        # Get the item being processed
        schedule_item = ScheduledAction.objects.get(id=s_item_id)

    # Check for exclude values and store them if needed
    schedule_item.exclude_values = payload.get('exclude_values', [])

    schedule_item.status = ScheduledAction.STATUS_PENDING
    schedule_item.save()

    # Create the payload to record the event in the log
    log_payload = {
        'action': schedule_item.action.name,
        'action_id': schedule_item.action.id,
        'execute': schedule_item.execute.isoformat(),
    }
    if schedule_item.action.action_type == Action.personalized_text:
        log_payload.update({
            'item_column': schedule_item.item_column.name,
            'subject': schedule_item.payload.get('subject'),
            'cc_email': schedule_item.payload.get('cc_email', []),
            'bcc_email': schedule_item.payload.get('bcc_email', []),
            'send_confirmation': schedule_item.payload.get(
                'send_confirmation',
                False),
            'track_read': schedule_item.payload.get('track_read', False),
        })
        log_type = Log.SCHEDULE_EMAIL_EDIT
    elif schedule_item.action.action_type == Action.send_list:
        log_payload.update({
            'email_to': schedule_item.payload.get('email_to'),
            'subject': schedule_item.payload.get('subject'),
            'cc_email': schedule_item.payload.get('cc_email', []),
            'bcc_email': schedule_item.payload.get('bcc_email', [])})
        log_type = Log.SCHEDULE_SEND_LIST_EDIT
    elif schedule_item.action.action_type == Action.personalized_json:
        ivalue = None
        if schedule_item.item_column:
            ivalue = schedule_item.item_column.name
        log_payload.update({
            'item_column': ivalue,
            'token': schedule_item.payload.get('subject'),
        })
        log_type = Log.SCHEDULE_JSON_EDIT
    elif schedule_item.action.action_type == Action.send_list_json:
        log_type = Log.SCHEDULE_JSON_LIST_EDIT
    elif schedule_item.action.action_type == Action.personalized_canvas_email:
        ivalue = None
        if schedule_item.item_column:
            ivalue = schedule_item.item_column.name
        log_payload.update({
            'item_column': ivalue,
            'token': schedule_item.payload.get('subject'),
            'subject': schedule_item.payload.get('subject'),
        })
        log_type = Log.SCHEDULE_CANVAS_EMAIL_EDIT
    else:
        messages.error(
            request,
            _('This type of actions cannot be scheduled'))
        return redirect('action:index')

    # Create the log
    Log.objects.register(
        request.user,
        log_type,
        schedule_item.action.workflow,
        log_payload)

    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    # Successful processing.
    return render(
        request,
        'scheduler/schedule_done.html',
        {
            'tdelta': create_timedelta_string(schedule_item.execute),
            's_item': schedule_item})
