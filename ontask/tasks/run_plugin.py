# -*- coding: utf-8 -*-

"""Function to run a plugin asynchronously."""
import logging
from typing import Dict, Optional

from django.utils.translation import ugettext

from ontask import models
from ontask.dataops.services.plugin_admin import run_plugin
from ontask.models import Plugin
from ontask.tasks.execute import task_execute_factory

logger = logging.getLogger('ontask')


class ExecuteRunPlugin(object):
    """Process the request to run a plugin in a workflow"""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.PLUGIN_EXECUTE

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Execute the plugin. Most of the parameters are in the payload.

        Execute the run method in a plugin with the dataframe from the given
        workflow and a payload with:

        - plugin_id: Id of the plugin being executed
        - input_column_names: List of input column names
        - output_column_names: List of output column names
        - output_suffix: Suffix that is added to the output column names
        - merge_key: Key column to use in the merge
        - parameters: Dictionary with the execution parameters
        """
        del action
        if not log_item and self.log_event:
            log_item = workflow.log(
                user,
                operation_type=self.log_event,
                **payload)

        try:
            # Get all the required information
            plugin_id = payload['plugin_id']
            input_column_names = payload['input_column_names']
            output_column_names = payload['output_column_names']
            output_suffix = payload['output_suffix']
            merge_key = payload['merge_key']
            parameters = payload['parameters']

            plugin_info = Plugin.objects.filter(pk=plugin_id).first()
            if not plugin_info:
                raise Exception(
                    ugettext('Unable to load plugin with id {pid}').format(
                        plugin_id),
                )

            # Set the status to "executing" before calling the function
            log_item.payload['status'] = 'Executing'
            log_item.save()

            # Invoke plugin execution
            run_plugin(
                workflow,
                plugin_info,
                input_column_names,
                output_column_names,
                output_suffix,
                merge_key,
                parameters)

            # Reflect status in the log event
            log_item.payload['status'] = 'Execution finished successfully'
            log_item.save()
        except Exception as exc:
            log_item.payload['status'] = ugettext('Error: {0}').format(str(exc))
            log_item.save()


task_execute_factory.register_producer(
    models.Log.PLUGIN_EXECUTE, ExecuteRunPlugin())
