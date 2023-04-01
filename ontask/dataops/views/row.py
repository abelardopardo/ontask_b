"""Functions to update and create a row in the dataframe."""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.core import (
    ONTASK_UPLOAD_FIELD_PREFIX, UserIsInstructor, WorkflowView)
from ontask.dataops import forms, services, sql


class RowCreateView(UserIsInstructor, WorkflowView, generic.FormView):
    """Process request to create a new row in the data table."""

    form_class = forms.RowForm
    template_name = 'dataops/row_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs['cancel_url'] = reverse('table:display')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        row_values = [
            form.cleaned_data[(ONTASK_UPLOAD_FIELD_PREFIX + '%s') % idx]
            for idx in range(self.workflow.columns.count())]
        try:
            services.create_row(self.workflow, row_values)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                self.request,
                'dataops/row_create.html',
                {'workflow': self.workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        self.workflow.log(
            self.request.user,
            models.Log.WORKFLOW_DATA_ROW_CREATE,
            new_values=list(
                zip([col.name for col in self.workflow.columns.all()],
                    [str(rval) for rval in row_values])))
        return redirect('table:display')


class RowUpdateView(UserIsInstructor, WorkflowView, generic.FormView):
    """Process request to update a row in the data table."""

    form_class = forms.RowForm
    template_name = 'dataops/row_filter.html'

    update_key = None
    update_val = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs['cancel_url'] = reverse('table:display')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        kwargs['initial_values'] = sql.get_row(
            self.workflow.get_data_frame_table_name(),
            key_name=self.update_key,
            key_value=self.update_val,
            column_names=self.workflow.get_column_names())
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return redirect('table:display')

        try:
            row_values = [
                form.cleaned_data[(ONTASK_UPLOAD_FIELD_PREFIX + '%s') % idx]
                for idx in range(self.workflow.columns.count())]
            services.update_row_values(
                self.workflow,
                self.update_key,
                self.update_val,
                row_values)
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(
                self.request,
                'dataops/row_filter.html',
                {'workflow': self.workflow,
                 'form': form,
                 'cancel_url': reverse('table:display')})

        self.workflow.log(
            self.request.user,
            models.Log.WORKFLOW_DATA_ROW_UPDATE,
            new_values=list(zip(
                [col.name for col in self.workflow.columns.all()],
                [str(rval) for rval in row_values])))
        return redirect('table:display')

    def dispatch(self, request, *args, **kwargs):
        self.update_key = request.GET.get('k')
        self.update_val = request.GET.get('v')

        if not self.update_key or not self.update_val:
            # Malformed request
            messages.error(request, _('Unable to update table row'))
            return redirect(reverse('home'))

        return super().dispatch(request, *args, **kwargs)
