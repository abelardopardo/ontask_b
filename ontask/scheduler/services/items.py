# -*- coding: utf-8 -*-

"""Service to manipulate items."""
from datetime import datetime
import json
from typing import Dict, Optional

from cron_descriptor import CasingTypeEnum, ExpressionDescriptor
from django.conf import settings
from django.forms.models import model_to_dict
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.translation import ugettext
import pytz

from ontask import models
from ontask.core import SessionPayload

DAYS_IN_YEAR = 365
SECONDS_IN_HOUR = 3600


def get_item_value_dictionary(sch_obj: models.ScheduledOperation) -> Dict:
    """Get a dictionary with the values in the time."""
    result = model_to_dict(sch_obj)
    result['item_column'] = str(sch_obj.item_column)
    result['workflow'] = str(sch_obj.workflow)
    result['action'] = str(sch_obj.action)
    result['payload'] = json.dumps(result['payload'], indent=2)
    result.pop('id')
    result.pop('user')
    result = {
        models.ScheduledOperation._meta.get_field(
            key).verbose_name.title(): val
        for key, val in result.items()}

    return result


def create_timedelta_string(
    ftime: datetime,
    frequency: str,
    utime: Optional[datetime] = None,
) -> Optional[str]:
    """Create a string rendering a time delta between now and the given one.

    The rendering proceeds gradually to see if the words days, hours, minutes
    etc. are needed.

    :param ftime: datetime object (may be in the past)
    :param frequency: string with the cron frequency (or empty)
    :param utime: until datetime object
    :return: String rendering
    """
    if not models.ScheduledOperation.validate_times(ftime, frequency, utime):
        return None

    now = datetime.now(pytz.timezone(settings.TIME_ZONE))

    if ftime and not frequency and not utime:
        # Single execution
        if ftime < now and not utime:
            return None

        return ftime.strftime('%H:%M:%S %z %Y/%b/%d')

    # Repeating execution.
    result = str(ExpressionDescriptor(
        frequency,
        casing_type=CasingTypeEnum.LowerCase))
    if not ftime and not utime:
        return result

    if ftime:
        # Has start time
        result = (
            ugettext('Starting at ')
            + ftime.strftime('%H:%M:%S %z %Y/%b/%d')
            + ', ' + result)

    if utime:
        # Has finish time
        result = result + ', until ' + utime.strftime('%H:%M:%S %z %Y/%b/%d')

    return result


def create_payload(
    request: HttpRequest,
    operation_type: str,
    prev_url: str,
    s_item: Optional[models.ScheduledOperation] = None,
    action: Optional[models.Action] = None,
) -> SessionPayload:
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
    payload = SessionPayload(
        request.session,
        initial_values={
            'action_id': action.id,
            'exclude_values': exclude_values,
            'operation_type': operation_type,
            'prev_url': prev_url,
            'post_url': reverse('scheduler:finish_scheduling'),
        })
    if s_item:
        payload.update(s_item.payload)
        payload['schedule_id'] = s_item.id
        payload['item_column'] = s_item.item_column.pk

    return payload


def delete_item(s_item: models.ScheduledOperation):
    """Delete a scheduled operation and log the event."""
    s_item.log(models.Log.SCHEDULE_DELETE)
    s_item.delete()
