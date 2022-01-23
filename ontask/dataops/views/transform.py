# -*- coding: utf-8 -*-

"""Views to manipulate the transformations and models."""

from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.celery import celery_is_up
from ontask.core import (
    ONTASK_UPLOAD_FIELD_PREFIX, UserIsInstructor, WorkflowView)
from ontask.dataops import forms, services


class TransformModelShowView(
    UserIsInstructor,
    WorkflowView,
    generic.TemplateView
):
    """Show the table of models."""

    template_name = 'dataops/transform_model.html'
    is_model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        table_err = None
        if self.request.user.is_superuser:
            table_err = models.Plugin.objects.filter(is_model=None)

        context.update({
            'table': services.create_model_table(
                self.request,
                self.workflow,
                self.is_model),
            'is_model': self.is_model,
            'table_err': table_err})
        return context


class PluginInvokeView(UserIsInstructor, WorkflowView, generic.FormView):
    """Render the view for the first step of plugin execution."""

    wf_pf_related = 'columns'
    form_class = forms.PluginInfoForm
    template_name = 'dataops/plugin_info_for_run.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        context.update({
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
            'pinstance': self.plugin_instance})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        kwargs['plugin_instance'] = self.plugin_instance
        return kwargs

    def form_valid(self, form):
        log_item = services.plugin_queue_execution(
            self.request,
            self.workflow,
            self.plugin_info,
            self.plugin_instance,
            {
                'columns': form.cleaned_data.get('columns'),
                'input_column_names': form.get_input_column_names(),
                'output_column_names': form.get_output_column_names(),
                'params': form.get_parameters(),
                'out_column_suffix': form.cleaned_data['out_column_suffix'],
                'merge_key': form.cleaned_data['merge_key']})

        # Successful processing.
        return render(
            self.request,
            'dataops/plugin_execution_report.html',
            {'log_id': log_item.id})

    def dispatch(self, request, *args, **kwargs):
        # Verify that celery is running!
        if not celery_is_up():
            messages.error(
                request,
                _(
                    'Unable to run plugins due to a misconfiguration. '
                    + 'Ask your system administrator to enable queueing.'))
            return redirect(reverse('table:display'))

        self.plugin_info = models.Plugin.objects.filter(
            pk=kwargs['pk']).first()
        if not self.plugin_info:
            return redirect('home')

        if self.workflow.nrows == 0:
            return render(
                request,
                'dataops/plugin_info_for_run.html',
                {'empty_wflow': True,
                 'is_model': self.plugin_info.get_is_model()})

        self.plugin_instance, __ = services.load_plugin(
            self.plugin_info.filename)
        if self.plugin_instance is None:
            messages.error(
                request,
                _('Unable to instantiate plugin "{0}"').format(
                    self.plugin_info.name),
            )
            return redirect('dataops:transform')

        return super().dispatch(request, *args, **kwargs)
