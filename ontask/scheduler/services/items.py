"""Service to manipulate scheduled items."""
import json
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo

from cron_descriptor import CasingTypeEnum, ExpressionDescriptor
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils.translation import gettext

from ontask import models


def get_item_value_dictionary(sch_obj: models.ScheduledOperation) -> Dict:
    """Get a dictionary with the values in the time."""
    result = model_to_dict(sch_obj)
    result['operation_type'] = models.Log.LOG_TYPES[result['operation_type']]
    if result['frequency']:
        result['frequency'] = str(ExpressionDescriptor(result['frequency']))
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

    :param ftime: datetime object (maybe in the past)
    :param frequency: string with the cron frequency (or empty)
    :param utime: until datetime object
    :return: String rendering
    """
    diagnostic_msg = models.ScheduledOperation.validate_times(
        ftime,
        frequency,
        utime)
    if diagnostic_msg:
        return None

    now = datetime.now(ZoneInfo(settings.TIME_ZONE))

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
            gettext('Starting at ')
            + ftime.strftime('%H:%M:%S %z %Y/%b/%d')
            + ', ' + result)

    if utime:
        # Has finish time
        result = result + ', until ' + utime.strftime('%H:%M:%S %z %Y/%b/%d')

    return result
