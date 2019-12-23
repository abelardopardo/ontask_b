# -*- coding: utf-8 -*-

"""Import packages and initialize the task_execute_factory."""
from ontask import models
from ontask.tasks.execute import execute_operation, task_execute_factory
from ontask.tasks.increase_track import ExecuteIncreaseTrackCount
from ontask.tasks.run_plugin import ExecuteRunPlugin
from ontask.tasks.scheduled_ops import execute_scheduled_operation
from ontask.tasks.workflow_update_luser import ExecuteUpdateWorkflowLUser


task_execute_factory.register_producer(
    models.Log.WORKFLOW_UPDATE_LUSERS,
    ExecuteUpdateWorkflowLUser())

task_execute_factory.register_producer(
    models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
    ExecuteIncreaseTrackCount())

task_execute_factory.register_producer(
    models.Log.PLUGIN_EXECUTE,
    ExecuteRunPlugin())
