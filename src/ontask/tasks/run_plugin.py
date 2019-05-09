from celery import shared_task
from django.utils.translation import ugettext

from dataops.models import PluginRegistry
from dataops.plugin.plugin_manager import run_plugin
from ontask.tasks.basic import get_execution_items, get_log_item


@shared_task
def run_plugin_task(
    user_id,
    workflow_id,
    plugin_id,
    input_column_names,
    output_column_names,
    output_suffix,
    merge_key,
    parameters,
    log_id):
    """

    Execute the run method in a plugin with the dataframe from the given
    workflow

    :param user_id: Id of User object that is executing the action
    :param workflow_id: Id of workflow being processed
    :param plugin_id: Id of the plugin being executed
    :param input_column_names: List of input column names
    :param output_column_names: List of output column names
    :param output_suffix: Suffix that is added to the output column names
    :param merge_key: Key column to use in the merge
    :param parameters: Dictionary with the parameters to execute the plug in
    :param log_id: Id of the log object where the status has to be reflected
    :return: Nothing, the result is stored in the log with log_id
    """

    # First get the log item to make sure we can record diagnostics
    log_item = get_log_item(log_id)
    if not log_item:
        return False

    to_return = True
    try:
        user, workflow, __ = get_execution_items(
            user_id=user_id,
            workflow_id=workflow_id)

        plugin_info = PluginRegistry.objects.filter(pk=plugin_id).first()
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
        to_return = False

    return to_return
