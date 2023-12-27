"""Import the view modules"""
from ontask.scheduler.views.crud import (
    ScheduledItemDelete, SchedulerIndexView, create_action_run,
    create_sql_upload, create_canvas_course_upload, edit_scheduled_operation,
    finish_scheduling, ScheduledItemToggleEnabledView)
from ontask.scheduler.views.index import SchedulerIndex
