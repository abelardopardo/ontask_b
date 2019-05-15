# -*- coding: utf-8 -*-


from builtins import object, range, str
import json
from typing import Optional

from celery.task.control import inspect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A
import django_tables2 as tables

from dataops.forms import FIELD_PREFIX, PluginInfoForm
from dataops.models import PluginRegistry
from dataops.plugin.plugin_manager import load_plugin, refresh_plugin_data
from logs.models import Log
from ontask.decorators import get_workflow
from ontask.permissions import is_instructor
from ontask.tasks import run_plugin_task
from workflow.models import Workflow


class PluginRegistryTable(tables.Table):
    """Class to render the table with plugins available for execution.

    The Operations column is inheriting from another class to centralise the
    customisation.
    """

    name = tables.Column(verbose_name=_('Name'), empty_values=None)

    description_txt = tables.TemplateColumn(
        verbose_name=_('Description'),
        template_name='dataops/includes/partial_plugin_description.html',
    )

    last_exec = tables.DateTimeColumn(verbose_name=_('Last executed'))

    def __init__(self, *args, **kwargs):
        """Set workflow and request."""
        self.workflow = kwargs.pop('workflow')
        self.request = kwargs.pop('request')

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

    def render_is_verified(self, record):
        """Render as an icon."""
        if record.is_verified:
            return format_html('<span class="true">✔</span>')

        return render_to_string(
            'dataops/includes/partial_plugin_diagnose.html',
            context={'id': record.id},
            request=None,
        )

    def render_last_exec(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        log_item = self.workflow.logs.filter(
            user=self.request.user,
            name=Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '--'
        return log_item.created

    class Meta(object):
        """Choose model, fields, sequence and attributes."""

        model = PluginRegistry

        fields = ('name', 'description_txt', 'is_verified')

        sequence = ('name', 'description_txt', 'is_verified', 'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'transform-table',
        }


@user_passes_test(is_instructor)
@get_workflow()
def uploadmerge(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show the table of options for upload/merge operation.

    :param request: Http Request

    :param workflow: To know if this is upload or merge.

    :return: Nothing
    """
    # Get the workflow that is being used
    return render(
        request,
        'dataops/uploadmerge.html',
        {'valuerange': range(5) if workflow.has_table() else range(3)})


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

    table = PluginRegistryTable(
        PluginRegistry.objects.filter(is_model=is_model),
        orderable=False,
        request=request,
        workflow=workflow,
    )

    return render(
        request,
        'dataops/transform_model.html',
        {'table': table, 'is_model': is_model})


@user_passes_test(is_instructor)
def diagnose(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show the diagnostics of a plugin that failed the verification tests.

    :param request: HTML request object

    :param pk: Primary key of the transform element

    :return:
    """
    # Action being used
    plugin = PluginRegistry.objects.filter(id=pk).first()
    if not plugin:
        return JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    pinstance, msgs = load_plugin(plugin.filename)

    # If the new instance is now properly verified, simply redirect to the
    # transform page
    if pinstance:
        plugin.is_verified = True
        plugin.save()
        return JsonResponse({'html_redirect': reverse('dataops:transform')})

    # Get the diagnostics from the plugin and use it for rendering.
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_diagnostics.html',
            {'diagnostic_table': msgs, 'folder': plugin.filename},
            request=request),
    })


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
    celery_stats = None
    try:
        celery_stats = inspect().stats()
    except Exception:
        # If the stats are empty, celery is not running.
        if not celery_stats:
            messages.error(
                request,
                _(
                    'Unable to run plugins due to a misconfiguration. '
                    + 'Ask your system administrator to enable queueing.'))
            return redirect(reverse('table:display'))

    plugin_info = PluginRegistry.objects.filter(pk=pk).first()
    if not plugin_info:
        return redirect('home')

    if workflow.nrows == 0:
        return render(
            request,
            'dataops/plugin_info_for_run.html',
            {'empty_wflow': True,
             'is_model': plugin_info.get_is_model()})

    plugin_instance, msgs = load_plugin(plugin_info.filename)
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

    # Set the basic elements in the context
    context = {
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
    }

    if request.method == 'POST' and form.is_valid():
        # Take the list of inputs from the form if empty list is given.
        input_column_names = []
        if plugin_instance.input_column_names:
            # Traverse the fields and get the names of the columns
            for idx, __ in enumerate(plugin_instance.input_column_names):
                cid = form.cleaned_data[FIELD_PREFIX + 'input_%s' % idx]
                input_column_names.append(
                    workflow.columns.get(wid=int(cid)).name,
                )
        else:
            input_column_names = [
                col.name for col in form.cleaned_data['columns']]

        output_column_names = []
        if plugin_instance.output_column_names:
            # Process the output columns
            for idx, __ in enumerate(plugin_instance.output_column_names):
                new_cname = form.cleaned_data[FIELD_PREFIX + 'output_%s' % idx]
                output_column_names.append(new_cname)
        else:
            # Plugin instance has an empty set of output files, clone the input
            output_column_names = input_column_names[:]

        suffix = form.cleaned_data['out_column_suffix']
        if suffix:
            # A suffix has been provided, add it to the list of outputs
            output_column_names = [
                cname + suffix for cname in output_column_names
            ]

        # Pack the parameters
        parameters = {}
        for idx, tpl in enumerate(plugin_instance.parameters):
            parameters[tpl[0]] = form.cleaned_data[
                FIELD_PREFIX + 'parameter_%s' % idx]

        # Log the event with the status "preparing invocation"
        log_item = Log.objects.register(
            request.user,
            Log.PLUGIN_EXECUTE,
            workflow,
            {
                'id': plugin_info.id,
                'name': plugin_info.name,
                'input_column_names': input_column_names,
                'output_column_names': output_column_names,
                'parameters': json.dumps(parameters, default=str),
                'status': 'preparing execution'})

        run_plugin_task.apply_async(
            (
                request.user.id,
                workflow.id,
                pk,
                input_column_names,
                output_column_names,
                suffix,
                form.cleaned_data['merge_key'],
                parameters,
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
        context)


@user_passes_test(is_instructor)
@get_workflow()
def moreinfo(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show the detailed information about a plugin.

    :param request: HTML request object

    :param pk: Primary key of the PluginRegistry element

    :return:
    """
    # Action being used
    plugin = PluginRegistry.objects.filter(id=pk).first()
    if not plugin:
        return JsonResponse({'html_redirect': reverse('home')})

    # Reload the plugin to get the messages stored in the right place.
    pinstance, msgs = load_plugin(plugin.filename)

    # Get the descriptions and show them in the modal
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_plugin_long_description.html',
            {'pinstance': pinstance},
            request=request),
    })
