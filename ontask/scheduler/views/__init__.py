# -*- coding: utf-8 -*-

"""Import the view modules"""
from ontask.scheduler.views.crud import (
    create_action_run, delete, edit_scheduled_operation,
    finish_scheduling, schedule_toggle, view)
from ontask.scheduler.views.index import index
from ontask.scheduler.views.sqlop import (
    schedule_sqlupload, sql_connection_index)
