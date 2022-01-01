# -*- coding: utf-8 -*-

"""Pages to edit the attributes."""

from django import http
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import models
from ontask.core import (
    JSONFormResponseMixin, WorkflowView, UserIsInstructor, ajax_required)
from ontask.workflow import forms, services


@method_decorator(ajax_required, name='dispatch')
class WorkflowAttributeCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.FormView,
):
    """View to create a new attribute in the workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.AttributeItemForm
    template_name = 'workflow/includes/partial_attribute_create.html'

    def get_context_data(self, **kwargs):
        """Add pk for the attribute to the context data."""
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def get_form_kwargs(self):
        """Store keys in form_kwargs"""
        form_kwargs = super().get_form_kwargs()
        form_kwargs['workflow'] = self.workflow
        keys = list(self.workflow.attributes.keys())
        form_kwargs['keys'] = keys
        pk = self.kwargs.get('pk')
        if pk is not None:
            form_kwargs['key'] = keys[pk]
            form_kwargs['value'] = self.workflow.attributes[keys[pk]]
        return form_kwargs

    def form_valid(self, form):
        """Store the attribute"""
        return services.save_attribute_form(
            self.request,
            form,
            self.kwargs.get('pk'))


class WorkflowAttributeEditView(WorkflowAttributeCreateView):
    """View to edit an existing attribute in a workflow."""

    template_name = 'workflow/includes/partial_attribute_edit.html'


@method_decorator(ajax_required, name='dispatch')
class WorkflowAttributeDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.TemplateView,
):
    """View to delete an existing attribute in a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_attribute_delete.html'

    def get_context_data(self, **kwargs):
        """Add pk and the key name to the context."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        context['key'], _ = list(
            self.workflow.attributes.items())[kwargs['pk']]
        return context

    def post(self, request, *args, **kwargs):
        """Perform the attribute delete operation."""
        wf_attributes = self.workflow.attributes
        key = sorted(wf_attributes.keys())[kwargs['pk']]
        wf_attributes.pop(key, None)
        self.workflow.attributes = wf_attributes
        self.workflow.log(
            request.user,
            models.Log.WORKFLOW_ATTRIBUTE_DELETE,
            **wf_attributes)
        self.workflow.save(update_fields=['attributes'])
        return http.JsonResponse({'html_redirect': ''})
