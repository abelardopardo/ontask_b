# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""

from datetime import datetime
from typing import Dict, Optional, Tuple

from croniter import croniter
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext, ugettext_lazy as _
import pytz

from ontask.action.payloads import (
    action_session_dictionary, set_action_payload,
)
from ontask.models import Action, Log, ScheduledAction
from ontask.scheduler.forms import (
    EmailScheduleForm, JSONListScheduleForm, JSONScheduleForm,
    SendListScheduleForm,
)

LOG_TYPE_DICT = {
    Action.PERSONALIZED_TEXT: Log.SCHEDULE_EMAIL_EDIT,
    Action.SEND_LIST: Log.SCHEDULE_SEND_LIST_EDIT,
    Action.PERSONALIZED_JSON: Log.SCHEDULE_JSON_EDIT,
    Action.SEND_LIST_JSON: Log.SCHEDULE_JSON_LIST_EDIT,
    Action.PERSONALIZED_CANVAS_EMAIL: Log.SCHEDULE_CANVAS_EMAIL_EDIT}

DAYS_IN_YEAR = 365
SECONDS_IN_HOUR = 3600


def create_timedelta_string(
    ftime: datetime,
    utime: Optional[datetime] = None,
) -> Tuple[bool, str]:
    """Create a string rendering a time delta between now and the given one.

    The rendering proceeds gradually to see if the words days, hours, minutes
    etc. are needed.

    :param ftime: datetime object (may be in the past)

    :param utime: until datetime object

    :return: String rendering
    """
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    if utime and utime < now:
        return False, ''

    if ftime < now and not utime:
        return False, ''

    dtime = ftime
    is_executing = False
    delta_string = []
    if ftime < now:
        is_executing = True
        ctab = str(
            settings.CELERY_BEAT_SCHEDULE['ontask_scheduler']['schedule'])
        citer = croniter(' '.join(ctab.split()[1:6]), now)
        dtime = citer.get_next(datetime)

    tdelta = dtime - now
    if tdelta.days // DAYS_IN_YEAR >= 1:
        delta_string.append(
            ugettext('{0} years').format(tdelta.days // DAYS_IN_YEAR))
    days = tdelta.days % DAYS_IN_YEAR
    if days != 0:
        delta_string.append(ugettext('{0} days').format(days))
    hours = tdelta.seconds // SECONDS_IN_HOUR
    if hours != 0:
        delta_string.append(ugettext('{0} hours').format(hours))
    minutes = (tdelta.seconds % SECONDS_IN_HOUR) // 60
    if minutes != 0:
        delta_string.append(ugettext('{0} minutes').format(minutes))

    return is_executing, ', '.join(delta_string)


def save_email_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict,
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
        form_info=op_payload)

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():
        if op_payload['confirm_items']:
            # Update information to carry to the filtering stage
            op_payload['button_label'] = ugettext('Schedule')
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            set_action_payload(request.session, op_payload)

            return redirect('action:item_filter')

        # Go straight to the final step
        return finish_scheduling(request, schedule_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
            'valuerange': range(2),
        },
    )


def save_send_list_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict,
) -> HttpResponse:
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
        instance=schedule_item,
        form_info=op_payload)

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():
        # Go straight to the final step
        return finish_scheduling(request, schedule_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
            'valuerange': range(2),
        },
    )


def save_json_schedule(
    request: HttpRequest,
    action: Action,
    schedule_item: ScheduledAction,
    op_payload: Dict,
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
        form_info=op_payload)

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():
        if op_payload['confirm_items']:
            # Create a dictionary in the session to carry over all the
            # information to execute the next steps
            op_payload['button_label'] = ugettext('Schedule')
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            set_action_payload(request.session, op_payload)

            return redirect('action:item_filter')

        # Go straight to the final step
        return finish_scheduling(request, schedule_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
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
        instance=schedule_item,
        form_info=op_payload)

    # Processing a valid POST request
    if request.method == 'POST' and form.is_valid():
        # Go straight to the final step
        return finish_scheduling(request, schedule_item, op_payload)

    # Render the form
    return render(
        request,
        'scheduler/edit.html',
        {
            'action': action,
            'form': form,
            'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
            'valuerange': range(2),
        },
    )


def finish_scheduling(
    request: HttpRequest,
    schedule_item: ScheduledAction = None,
    payload: Dict = None,
):
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
    s_item_id = payload.pop('schedule_id', None)
    action = Action.objects.get(pk=payload.pop('action_id'))
    column_name = payload.pop('item_column', None)
    column = None
    if column_name:
        column = action.workflow.columns.get(name=column_name)

    # Clean up some parameters from the payload
    payload = {
        key: payload[key]
        for key in payload if key not in [
            'button_label',
            'valuerange',
            'step',
            'prev_url',
            'post_url',
            'confirm_items']}

    # Create the payload to record the event in the log
    log_payload = payload.copy()

    if s_item_id:
        # Get the item being processed
        if not schedule_item:
            schedule_item = ScheduledAction.objects.filter(
                id=s_item_id).first()
        if not schedule_item:
            messages.error(
                None,
                _('Incorrect request in action scheduling'))
            return redirect('action:index')
        schedule_item.name = payload.pop('name')
        schedule_item.description_text = payload.pop('description_text')
        schedule_item.item_column = column
        schedule_item.execute = parse_datetime(payload.pop('execute'))
        schedule_item.execute_until = parse_datetime(
            payload.pop('execute_until'))
        schedule_item.exclude_values = payload.pop('exclude_values', [])
    else:
        schedule_item = ScheduledAction(
            user=request.user,
            action=action,
            name=payload.pop('name'),
            description_text=payload.pop('description_text'),
            item_column=column,
            execute=parse_datetime(payload.pop('execute')),
            execute_until=parse_datetime(payload.pop('execute_until')),
            exclude_values=payload.pop('exclude_values', []))

    # Check for exclude
    schedule_item.status = ScheduledAction.STATUS_PENDING
    schedule_item.payload = payload
    schedule_item.save()

    # Create the payload to record the event in the log
    log_type = LOG_TYPE_DICT.get(schedule_item.action.action_type)
    if not log_type:
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
    is_executing, tdelta = create_timedelta_string(
        schedule_item.execute,
        schedule_item.execute_until)
    return render(
        request,
        'scheduler/schedule_done.html',
        {
            'is_executing': is_executing,
            'tdelta': tdelta,
            's_item': schedule_item})


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
    del action, schedule_item, op_payload
    return render(request, 'under_construction.html', {})
