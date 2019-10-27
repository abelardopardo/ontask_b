# -*- coding: utf-8 -*-

"""Service to manipulate items."""
import json
from datetime import datetime
from typing import Dict, Optional

import pytz
from croniter import croniter
from django.conf import settings
from django.forms.models import model_to_dict
from django.http.request import HttpRequest
from django.urls.base import reverse
from django.utils.translation import ugettext

from ontask.action.payloads import (
    PAYLOAD_SESSION_DICTIONARY, set_action_payload,
)
from ontask.models import Action, Log, ScheduledOperation

DAYS_IN_YEAR = 365
SECONDS_IN_HOUR = 3600


def get_item_value_dictionary(sch_obj: ScheduledOperation) -> Dict:
    """Get a dictionary with the values in the time."""
    item_values = model_to_dict(sch_obj)
    item_values['item_column'] = str(sch_obj.item_column)
    item_values['workflow'] = str(sch_obj.workflow)
    item_values['action'] = str(sch_obj.action)
    item_values.pop('id')
    item_values.pop('user')
    item_values['payload'] = json.dumps(item_values['payload'], indent=2)

    return item_values


def create_timedelta_string(
    ftime: datetime,
    utime: Optional[datetime] = None,
) -> Optional[str]:
    """Create a string rendering a time delta between now and the given one.

    The rendering proceeds gradually to see if the words days, hours, minutes
    etc. are needed.

    :param ftime: datetime object (may be in the past)

    :param utime: until datetime object

    :return: String rendering
    """
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    if utime and utime < now:
        return None

    if ftime < now and not utime:
        return None

    dtime = ftime
    delta_string = []
    if ftime < now:
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

    return ', '.join(delta_string)


def create_payload(
    request: HttpRequest,
    operation_type: str,
    prev_url: str,
    s_item: Optional[ScheduledOperation] = None,
    action: Optional[Action] = None,
) -> Dict:
    """Create a payload dictionary to store in the session.

    :param request: HTTP request

    :param operation_type: String denoting the type of s_item being processed

    :param prev_url: String with the URL to use to "go back"

    :param s_item: Existing schedule item being processed (Optional)

    :param action: Corresponding action for the schedule operation type, or
    if empty, it is contained in the scheduled_item (Optional)

    :return: Dictionary with pairs name: value
    """
    if s_item:
        action = s_item.action
        exclude_values = s_item.exclude_values
    else:
        exclude_values = []

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(PAYLOAD_SESSION_DICTIONARY)
    if not op_payload:
        op_payload = {
            'action_id': action.id,
            'prev_url': prev_url,
            'post_url': reverse(
                'scheduler:finish_scheduling'),
            'exclude_values': exclude_values,
            'operation_type': operation_type}
        if s_item:
            op_payload.update(s_item.payload)
        set_action_payload(request.session, op_payload)
        request.session.save()

    if s_item:
        op_payload['schedule_id'] = s_item.id

    return op_payload


def delete_item(s_item: ScheduledOperation):
    """Delete a scheduled operation and log the event."""
    s_item.log(Log.SCHEDULE_DELETE)
    s_item.delete()
