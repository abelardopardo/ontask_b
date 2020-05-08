# -*- coding: utf-8 -*-

"""All services for scheduled operation objects."""
from ontask.scheduler.services.action_producers import (
    ScheduledOperationSaveEmail, ScheduledOperationSaveEmailReport,
    ScheduledOperationSaveJSON, ScheduledOperationSaveJSONReport,
)
from ontask.scheduler.services.crud_factory import schedule_crud_factory
from ontask.scheduler.services.errors import OnTaskScheduleIncorrectTimes
from ontask.scheduler.services.items import (
    create_timedelta_string, delete_item, get_item_value_dictionary,
)
from ontask.scheduler.services.scheduler_table import ScheduleActionTable
from ontask.scheduler.services.sql_producer import (
    ScheduledOperationSaveSQLUpload,
)
from ontask.scheduler.services.tasks_ops import schedule_task
