# -*- coding: utf-8 -*-

from ontask.tasks.basic import run_task
from ontask.tasks.dataupload import athena_dataupload_task
from ontask.tasks.increase_track import increase_track_count_task
from ontask.tasks.run_plugin import run_plugin_task
from ontask.tasks.scheduled_ops import execute_scheduled_actions_task
from ontask.tasks.workflow_update_luser import workflow_update_lusers_task
