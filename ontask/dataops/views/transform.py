# -*- coding: utf-8 -*-

"""Views to manipulate the transformations and models."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.urls import resolve
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.celery import celery_is_up
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX, get_workflow, is_instructor
from ontask.dataops import forms, services


@user_passes_test(is_instructor)
@get_workflow()
def transform_model(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Show the table of models.

    :param request: HTTP Request
    :param workflow: Object to apply the models.
    :return:
    """
    url_name = resolve(request.path).url_name
    is_model = url_name == 'model'

    table_err = None
    if request.user.is_superuser:
        table_err = models.Plugin.objects.filter(is_model=None)

    return render(
        request,
        'dataops/transform_model.html',
        {
            'table': services.create_model_table(request, workflow, is_model),
            'is_model': is_model,
            'table_err': table_err})


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def plugin_invoke(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Render the view for the first step of plugin execution.

    :param request: HTTP request received
    :param pk: primary key of the plugin
    :param workflow: Workflow being manipulated
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

    plugin_info = models.Plugin.objects.filter(pk=pk).first()
    if not plugin_info:
        return redirect('home')

    if workflow.nrows == 0:
        return render(
            request,
            'dataops/plugin_info_for_run.html',
            {'empty_wflow': True,
             'is_model': plugin_info.get_is_model()})

    plugin_instance, __ = services.load_plugin(plugin_info.filename)
    if plugin_instance is None:
        messages.error(
            request,
            _('Unable to instantiate plugin "{0}"').format(plugin_info.name),
        )
        return redirect('dataops:transform')

    # create the form to select the columns and the corresponding dictionary
    form = forms.PluginInfoForm(
        request.POST or None,
        workflow=workflow,
        plugin_instance=plugin_instance)

    if request.method == 'POST' and form.is_valid():
        log_item = services.plugin_queue_execution(
            request,
            workflow,
            plugin_info,
            plugin_instance,
            {
                'columns': form.cleaned_data.get('columns'),
                'input_column_names': form.get_input_column_names(),
                'output_column_names': form.get_output_column_names(),
                'params': form.get_parameters(),
                'out_column_suffix': form.cleaned_data['out_column_suffix'],
                'merge_key': form.cleaned_data['merge_key']})

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
                if fld.name.startswith(ONTASK_UPLOAD_FIELD_PREFIX + 'input')],
            'output_column_fields': [
                fld for fld in list(form)
                if fld.name.startswith(ONTASK_UPLOAD_FIELD_PREFIX + 'output')],
            'parameters': [
                fld for fld in list(form)
                if fld.name.startswith(
                    ONTASK_UPLOAD_FIELD_PREFIX + 'parameter')],
            'pinstance': plugin_instance,
            'id': workflow.id,
        })
