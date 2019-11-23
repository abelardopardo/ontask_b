# -*- coding: utf-8 -*-

"""Service functions to handle plugin invocations."""

import json
from typing import Dict, List, Tuple

import django_tables2 as tables
from django import http
from django.db.models.expressions import F
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ontask import models, tasks
from ontask.dataops.forms import FIELD_PREFIX, PluginInfoForm
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

    def render_name(self, record):
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

    def render_last_exec(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        log_item = self.workflow.logs.filter(
            user=self.user,
            name=models.Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '--'
        return log_item.created

    class Meta(object):
        """Choose fields, sequence and attributes."""

        model = models.Plugin

        fields = ('name', 'description_text')

        sequence = ('name', 'description_text', 'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'transform-table',
        }


def _prepare_plugin_input_output(
    plugin_instance: OnTaskPluginAbstract,
    workflow: models.Workflow,
    form: PluginInfoForm,
) -> Tuple[List, List]:
    """Prepare input, output and parameters for plugin execution.

    :param plugin_instance: Plugin object allowed to execute

    :param workflow: Workflow object (to access columns and similar)

    :param form: Form just populated with a POST

    :return: [list of inputs, list of outputs]
    """
    # Take the list of inputs from the form if empty list is given.
    input_column_names = []
    if plugin_instance.input_column_names:
        # Traverse the fields and get the names of the columns
        for idx, __ in enumerate(plugin_instance.input_column_names):
            input_column_names.append(
                workflow.columns.get(id=int(
                    form.cleaned_data[FIELD_PREFIX + 'input_%s' % idx],
                )).name,
            )
    else:
        input_column_names = [col.name for col in form.cleaned_data['columns']]

    output_column_names = []
    if plugin_instance.output_column_names:
        # Process the output columns
        for idx, __ in enumerate(plugin_instance.output_column_names):
            output_column_names.append(
                form.cleaned_data[FIELD_PREFIX + 'output_%s' % idx])
    else:
        # Plugin instance has an empty set of output files, clone the input
        output_column_names = input_column_names[:]

    suffix = form.cleaned_data['out_column_suffix']
    if suffix:
        # A suffix has been provided, add it to the list of outputs
        output_column_names = [
            cname + suffix for cname in output_column_names
        ]

    return input_column_names, output_column_names


def _prepare_plugin_parameters(
    plugin_instance: OnTaskPluginAbstract,
    form: PluginInfoForm,
) -> Dict:
    # Pack the parameters
    exec_params = {}
    for idx, tpl in enumerate(plugin_instance.parameters):
        exec_params[tpl[0]] = form.cleaned_data[
            FIELD_PREFIX + 'parameter_%s' % idx]

    return exec_params


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
    refresh_plugin_data(request, workflow)

    return PluginAvailableTable(
        models.Plugin.objects.filter(
            is_model=is_model,
            is_verified=True,
            is_enabled=True),
        orderable=False,
        user=request.user,
        workflow=workflow)


def plugin_run(
    request: http.HttpRequest,
    workflow: models.Workflow,
    plugin_info: models.Plugin,
    plugin_instance: OnTaskPluginAbstract,
    form: PluginInfoForm,
) -> models.Log:
    """Batch execute the given instance of the plugin.

    :param request: Received request to process
    :param workflow: Current workflow being manipulated
    :param plugin_info: Information about the plugin in the DB
    :param plugin_instance: Instance of the class to execute
    :param form: form received
    :return:
    """
    in_cols, out_cols = _prepare_plugin_input_output(
        plugin_instance,
        workflow,
        form)

    exec_params = _prepare_plugin_parameters(
        plugin_instance,
        form)

    # Log the event with the status "preparing invocation"

    log_item = plugin_info.log(
        request.user,
        models.Log.PLUGIN_EXECUTE,
        input_column_names=in_cols,
        output_column_names=out_cols,
        parameters=json.dumps(exec_params, default=str),
        status='preparing execution')

    tasks.execute_operation.delay(
        models.Log.PLUGIN_EXECUTE,
        user_id=request.user.id,
        log_id=log_item.id,
        workflow_id=workflow.id,
        payload={
            'plugin_id': plugin_info.pk,
            'input_column_names': in_cols,
            'output_column_names': out_cols,
            'output_suffix': form.cleaned_data['out_column_suffix'],
            'merge_key': form.cleaned_data['merge_key'],
            'parameters': exec_params})

    return log_item
