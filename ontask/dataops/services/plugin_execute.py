"""Service functions to execute a plugin."""
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo

import pandas as pd
from django.conf import settings
from django.utils.translation import gettext

from ontask import OnTaskServiceException, models
from ontask.dataops import pandas
from ontask.dataops.services import load_plugin


def _execute_plugin(
    workflow,
    plugin_info,
    input_column_names,
    output_column_names,
    output_suffix,
    merge_key,
    plugin_params,
):
    """
    Execute the run method in the plugin.

    Execute the run method in a plugin with the dataframe from the given
    workflow

    :param workflow: Workflow object being processed
    :param plugin_info: PluginRegistry object being processed
    :param input_column_names: List of input column names
    :param output_column_names: List of output column names
    :param output_suffix: Suffix that is added to the output column names
    :param merge_key: Key column to use in the merge
    :param plugin_params: Dictionary with the parameters to execute the plug in
    :return: Nothing, the result is stored in the log with log_id
    """
    try:
        plugin_instance, msgs = load_plugin(plugin_info.filename)
    except OnTaskServiceException:
        raise Exception(
            gettext('Unable to instantiate plugin "{0}"').format(
                plugin_info.name),
        )

    # Check that the list of given inputs is consistent: if plugin has a list
    # of inputs, it has to have the same length as the given list.
    if (
        plugin_instance.get_input_column_names()
        and len(plugin_instance.get_input_column_names())
        != len(input_column_names)
    ):
        raise Exception(
            gettext(
                'Inconsistent number of inputs when invoking plugin "{0}"',
            ).format(plugin_info.name),
        )

    # Check that the list of given outputs has the same length as the list of
    # outputs proposed by the plugin
    if (
        plugin_instance.get_output_column_names()
        and len(plugin_instance.get_output_column_names())
        != len(output_column_names)
    ):
        raise Exception(
            gettext(
                'Inconsistent number of outputs when invoking plugin "{0}"',
            ).format(plugin_info.name),
        )

    # Get the data frame from the workflow
    try:
        df = pandas.load_table(workflow.get_data_frame_table_name())
    except Exception as exc:
        raise Exception(
            gettext(
                'Exception when retrieving the data frame from workflow: {0}',
            ).format(str(exc)),
        )

    # Set the updated names of the input, output columns, and the suffix
    if not plugin_instance.get_input_column_names():
        plugin_instance.input_column_names = input_column_names
    plugin_instance.output_column_names = output_column_names
    plugin_instance.output_suffix = output_suffix

    # Create a new dataframe with the given input columns, and rename them if
    # needed
    try:
        sub_df = pd.DataFrame(df[input_column_names])
        if plugin_instance.get_input_column_names():
            sub_df.columns = plugin_instance.get_input_column_names()
    except Exception as exc:
        raise Exception(gettext(
            'Error when creating data frame for plugin: {0}',
        ).format(str(exc)))

    # Try the execution and catch any exception
    try:
        new_df = plugin_instance.run(sub_df, parameters=plugin_params)
    except Exception as exc:
        raise Exception(
            gettext('Error while executing plugin: {0}').format(str(exc)),
        )

    # If plugin does not return a data frame, flag as error
    if not isinstance(new_df, pd.DataFrame):
        raise Exception(
            gettext(
                'Plugin executed but did not return a pandas data frame.'),
        )

    # Execution is DONE. Now we have to perform various additional checks

    # Result has to have the exact same number of rows
    if new_df.shape[0] != df.shape[0]:
        raise Exception(
            gettext(
                'Incorrect number of rows ({0}) in result data frame.',
            ).format(new_df.shape[0]),
        )

    # Merge key name cannot be part of the output df
    if merge_key in new_df.columns:
        raise Exception(
            gettext(
                'Column name {0} cannot be in the result data frame.'.format(
                    merge_key)),
        )

    # Result column names are consistent
    if set(new_df.columns) != set(plugin_instance.get_output_column_names()):
        raise Exception(gettext('Incorrect columns in result data frame.'))

    # Add the merge column to the result df
    new_df[merge_key] = df[merge_key]

    # Proceed with the merge
    try:
        new_frame = pandas.perform_dataframe_upload_merge(
            workflow,
            df,
            new_df,
            {
                'how_merge': 'inner',
                'dst_selected_key': merge_key,
                'src_selected_key': merge_key,
                'initial_column_names': list(new_df.columns),
                'rename_column_names': list(new_df.columns),
                'columns_to_upload': [True] * len(list(new_df.columns)),
            },
        )
    except Exception as exc:
        raise Exception(
            gettext('Error while merging result: {0}.').format(str(exc)),
        )

    if isinstance(new_frame, str):
        raise Exception(
            gettext('Error while merging result: {0}.').format(new_frame))

    # Update execution time in the plugin
    plugin_info.executed = datetime.now(
        ZoneInfo(settings.TIME_ZONE),
    )
    plugin_info.save(update_fields=['executed'])

    return True


class ExecuteRunPlugin:
    """Process the request to run a plugin in a workflow."""

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

        - plugin_id: Identifier of the plugin being executed
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

            plugin_info = models.Plugin.objects.filter(pk=plugin_id).first()
            if not plugin_info:
                raise Exception(
                    gettext('Unable to load plugin with id {pid}').format(
                        plugin_id),
                )

            # Set the status to "executing" before calling the function
            log_item.payload['status'] = 'Executing'
            log_item.save(update_fields=['payload'])

            # Invoke plugin execution
            _execute_plugin(
                workflow,
                plugin_info,
                input_column_names,
                output_column_names,
                output_suffix,
                merge_key,
                parameters)

            # Reflect status in the log event
            log_item.payload['status'] = 'Execution finished successfully'
            log_item.save(update_fields=['payload'])
        except Exception as exc:
            log_item.payload['status'] = gettext(
                'Error: {0}').format(str(exc))
            log_item.save(update_fields=['payload'])
