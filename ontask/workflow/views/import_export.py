# -*- coding: utf-8 -*-

"""Views to import/export a workflow."""
from builtins import str

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.core import RequestWorkflowView, UserIsInstructor
from ontask.workflow import forms, services


class WorkflowExportView(
    UserIsInstructor,
    RequestWorkflowView,
    generic.FormView,
):
    """View to request information to export a workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.WorkflowExportRequestForm
    template_name = 'workflow/export.html'
    pf_related = 'actions'
    only_action_list = False

    def get_context_data(self, **kwargs):
        """Store the workflow in the context."""
        context = super().get_context_data(**kwargs)

        context['workflow'] = self.workflow
        context['only_action_list'] = self.only_action_list
        return context

    def get_form_kwargs(self):
        """Set some required parameters in the form context."""
        form_kwargs = super().get_form_kwargs()

        form_kwargs['workflow'] = self.workflow

        return form_kwargs

    def form_valid(self, form):
        """Render export done page and prepare for download."""
        to_include = []
        for idx, a_id in enumerate(
            self.workflow.actions.values_list('id', flat=True),
        ):
            if form.cleaned_data['select_%s' % idx]:
                to_include.append(str(a_id))

        if not to_include and self.only_action_list:
            return redirect(reverse('action:index'))

        # Render the export done page with the url to trigger the download
        return render(
            self.request,
            'workflow/export_done.html',
            {
                'include': ','.join(to_include),
                'only_action_list': self.only_action_list})


class WorkflowActionExportView(WorkflowExportView):
    """View to request information to export a set of actions."""

    only_action_list = True

    def get_context_data(self, **kwargs):
        """Store the workflow in the context."""
        context = super().get_context_data(**kwargs)
        context['only_action_list'] = True
        return context


class WorkflowExportDoneView(UserIsInstructor, RequestWorkflowView):
    """View for downloading the exported workflow."""

    http_method_names = ['get']
    pf_related = 'actions'

    def get(self, request, *args, **kwargs):
        """Extract ids from URL and return ZIP download response"""
        page_data = kwargs['page_data']
        try:
            action_ids = [
                int(a_idx) for a_idx in page_data.split(',') if a_idx]
        except ValueError:
            return redirect('home')

        return services.do_export_workflow(self.workflow, action_ids)


class WorkflowImportView(UserIsInstructor, generic.FormView):
    """View to request information to export a workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.WorkflowImportForm
    template_name = 'workflow/import.html'

    def get_form_kwargs(self):
        """Store user in form_kwargs"""
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def form_valid(self, form):
        """Upload the file."""

        try:
            workflow = services.do_import_workflow(
                self.request.user,
                form.cleaned_data['name'],
                self.request.FILES['wf_file'])
            messages.success(
                self.request,
                _('Workflow {0} successfully imported.'.format(workflow.name))
            )
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)

        # Go back to the list of workflows
        return redirect('home')
