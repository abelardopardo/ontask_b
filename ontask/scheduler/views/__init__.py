# -*- coding: utf-8 -*-

"""Import the view modules"""
from ontask.scheduler.views.crud import (
    ScheduledItemDelete, SchedulerIndexView, create_action_run,
    create_sql_upload, edit_scheduled_operation, finish_scheduling,
    ActionToggleQuestionChangeView)
from ontask.scheduler.views.index import (
    SchedulerConnectionIndex, SchedulerIndex)
