# -*- coding: utf-8 -*-

"""Service functions to manage and check plugin compliance."""
import datetime
import json
from typing import Dict, Union

from django import http
from django.db.models.expressions import F
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import models, tasks
from ontask.dataops.plugin.ontask_plugin import OnTaskPluginAbstract
from ontask.dataops.services.plugin_admin import refresh_plugin_data


class PluginAvailableTable(tables.Table):
    """Class to render the table with plugins available for execution.

    The Operations column is inheriting from another class to centralise the
    customisation.
    """

    description_text = tables.TemplateColumn(
        verbose_name=_('Description'),
        template_name='dataops/includes/partial_plugin_description.html',
    )

    last_exec = tables.DateTimeColumn(verbose_name=_('Last executed'))

    def __init__(self, *args, **kwargs):
        """Set workflow and user to get latest execution time."""
        self.workflow = kwargs.pop('workflow')
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

    @staticmethod
    def render_name(record):
        """Render as a link or empty if it has not been verified."""
        if record.is_verified:
            return format_html(
                '<a href="{0}" '
                + 'data-toggle="tooltip" title="{1}">{2}',
                reverse('dataops:plugin_invoke', kwargs={'pk': record.id}),
                _('Execute the transformation'),
                record.name,
            )

        return record.filename

    def render_last_exec(self, record) -> Union[str, datetime.datetime]:
        """Render the last executed time.

        :param record: Record being processed in the table.
        :return: Datetime/string
        """
        log_item = self.workflow.logs.filter(
            user=self.user,
            name=models.Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '--'
        return log_item.created

    class Meta:
        """Choose fields, sequence and attributes."""

        model = models.Plugin

        fields = ('name', 'description_text')

        sequence = ('name', 'description_text', 'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'transform-table',
        }


def create_model_table(
    request: http.HttpRequest,
    workflow: models.Workflow,
    is_model: bool,
):
    """Create the table of plugins that are models.

    :param request: Received request
    :param workflow: Workflow being processed
    :param is_model: Is the object a model?
    :return: Table with available model plugins
    """
    # Traverse the plugin folder and refresh the db content.
    refresh_plugin_data(request)

    return PluginAvailableTable(
        models.Plugin.objects.filter(
            is_model=is_model,
            is_verified=True,
            is_enabled=True),
        orderable=False,
        user=request.user,
        workflow=workflow)


def plugin_queue_execution(
    request: http.HttpRequest,
    workflow: models.Workflow,
    plugin_info: models.Plugin,
    plugin_instance: OnTaskPluginAbstract,
    run_parameters: Dict,
) -> models.Log:
    """Put in the batch queue the execution of a plugin.

    :param request: Received request to process
    :param workflow: Current workflow being manipulated
    :param plugin_info: Information about the plugin in the DB
    :param plugin_instance: Instance of the class to execute
    :param run_parameters: Dictionary with all the required parameters
    :return:
    """
    # If the plugin has no inputs, copy the columns field.
    input_column_names = run_parameters['input_column_names']
    if not plugin_instance.input_column_names:
        input_column_names = [col.name for col in run_parameters['columns']]

    # If there are no output columns, clone the input
    output_column_names = run_parameters['output_column_names']
    if not plugin_instance.output_column_names:
        # Plugin instance has an empty set of output files, clone the input
        output_column_names = run_parameters['input_column_names'][:]

    suffix = run_parameters['out_column_suffix']
    if suffix:
        # A suffix has been provided, add it to the list of outputs
        output_column_names = [
            cname + suffix for cname in run_parameters['output_column_names']]

    # Log the event with the status "preparing invocation"
    log_item = plugin_info.log(
        request.user,
        models.Log.PLUGIN_EXECUTE,
        input_column_names=input_column_names,
        output_column_names=output_column_names,
        parameters=json.dumps(run_parameters['params'], default=str),
        status='preparing execution')

    tasks.execute_operation.delay(
        models.Log.PLUGIN_EXECUTE,
        user_id=request.user.id,
        log_id=log_item.id,
        workflow_id=workflow.id,
        payload={
            'plugin_id': plugin_info.pk,
            'input_column_names': input_column_names,
            'output_column_names': output_column_names,
            'output_suffix': run_parameters['out_column_suffix'],
            'merge_key': run_parameters['merge_key'],
            'parameters': run_parameters['params']})

    return log_item
