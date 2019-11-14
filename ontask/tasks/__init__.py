# -*- coding: utf-8 -*-

from ontask.tasks.dataupload import athena_dataupload_task
from ontask.tasks.scheduled_ops import execute_scheduled_operations_task
from ontask.tasks.execute import task_execute_factory, execute_operation
from ontask.tasks.increase_track import ExecuteIncreaseTrackCount
from ontask.tasks.run_plugin import ExecuteRunPlugin
from ontask.tasks.workflow_update_luser import ExecuteUpdateWorkflowLUser
