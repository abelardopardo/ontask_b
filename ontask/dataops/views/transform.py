# -*- coding: utf-8 -*-

"""Views to manipulate the transformations and models."""

import json
from builtins import object, str
from typing import Dict, List, Optional, Tuple

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.urls import resolve
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ontask.core.celery import celery_is_up
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.forms import FIELD_PREFIX, PluginInfoForm
from ontask.dataops.plugin.plugin_manager import (
    load_plugin, refresh_plugin_data,
)
from ontask.models import Log, Plugin, Workflow
from ontask.tasks import run_plugin_task


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
            name=Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '--'
        return log_item.created

    class Meta(object):
        """Choose fields, sequence and attributes."""

        model = Plugin

        fields = ('name', 'description_text')

        sequence = ('name', 'description_text', 'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'transform-table',
        }


def _prepare_plugin_input_output(
    plugin_instance: Plugin,
    workflow: Workflow,
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
    plugin_instance: Plugin,
    form: PluginInfoForm,
) -> Dict:
    # Pack the parameters
    exec_params = {}
    for idx, tpl in enumerate(plugin_instance.parameters):
        exec_params[tpl[0]] = form.cleaned_data[
            FIELD_PREFIX + 'parameter_%s' % idx]

    return exec_params


@user_passes_test(is_instructor)
@get_workflow()
def transform_model(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show the table of models.

    :param request: HTTP Request

    :param workflow: Object to apply the models.

    :return:
    """
    # Get the workflow that is being used
    url_name = resolve(request.path).url_name
    is_model = url_name == 'model'

    # Traverse the plugin folder and refresh the db content.
    refresh_plugin_data(request, workflow)

    table_ok = PluginAvailableTable(
        Plugin.objects.filter(
            is_model=is_model,
            is_verified=True,
            is_enabled=True),
        orderable=False,
        user=request.user,
        workflow=workflow)

    table_err = None
    if request.user.is_superuser:
        table_err = Plugin.objects.filter(is_model=None)

    return render(
        request,
        'dataops/transform_model.html',
        {'table': table_ok, 'is_model': is_model, 'table_err': table_err})


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def plugin_invoke(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the view for the first step of plugin execution.

    :param request: HTTP request received
    :param pk: primary key of the plugin
    :return: Page offering to select the columns to invoke
    """
    # Verify that celery is running!
    if not celery_is_up():
        messages.error(
            request,
            _(
                'Unable to run plugins due to a misconfiguration. '
                + 'Ask your system administrator to enable queueing.'))
        return redirect(reverse('table:display'))

    plugin_info = Plugin.objects.filter(pk=pk).first()
    if not plugin_info:
        return redirect('home')

    if workflow.nrows == 0:
        return render(
            request,
            'dataops/plugin_info_for_run.html',
            {'empty_wflow': True,
             'is_model': plugin_info.get_is_model()})

    plugin_instance, __ = load_plugin(plugin_info.filename)
    if plugin_instance is None:
        messages.error(
            request,
            _('Unable to instantiate plugin "{0}"').format(plugin_info.name),
        )
        return redirect('dataops:transform')

    # create the form to select the columns and the corresponding dictionary
    form = PluginInfoForm(
        request.POST or None,
        workflow=workflow,
        plugin_instance=plugin_instance)

    if request.method == 'POST' and form.is_valid():
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
            Log.PLUGIN_EXECUTE,
            input_column_names=in_cols,
            output_column_names=out_cols,
            parameters=json.dumps(exec_params, default=str),
            status='preparing execution')

        run_plugin_task.apply_async(
            (
                request.user.id,
                workflow.id,
                pk,
                in_cols,
                out_cols,
                form.cleaned_data['out_column_suffix'],
                form.cleaned_data['merge_key'],
                exec_params,
                log_item.id),
            serializer='pickle')

        # Successful processing.
        return render(
            request,
            'dataops/plugin_execution_report.html',
            {'log_id': log_item.id})

    return render(
        request,
        'dataops/plugin_info_for_run.html',
        context={
            'form': form,
            'input_column_fields': [
                fld for fld in list(form)
                if fld.name.startswith(FIELD_PREFIX + 'input')],
            'output_column_fields': [
                fld for fld in list(form)
                if fld.name.startswith(FIELD_PREFIX + 'output')],
            'parameters': [
                fld for fld in list(form)
                if fld.name.startswith(FIELD_PREFIX + 'parameter')],
            'pinstance': plugin_instance,
            'id': workflow.id,
        })
