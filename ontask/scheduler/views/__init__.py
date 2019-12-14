# -*- coding: utf-8 -*-

"""Import the view modules"""
from ontask.scheduler.views.crud import (
    create_action_run, create_workflow_op, delete, edit_scheduled_operation,
    finish_scheduling, schedule_toggle, view)
from ontask.scheduler.views.index import index
