# -*- coding: utf-8 -*-

"""Views implementing CRUD operations with workflows."""

from django import http
from django.contrib import messages
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.celery import celery_is_up
from ontask.core import (
    JSONFormResponseMixin, WorkflowView,
    UserIsInstructor, ajax_required, remove_workflow_from_session)
from ontask.workflow import forms, services


class WorkflowIndexView(UserIsInstructor, generic.ListView):
    """View to list user workflows."""

    http_method_names = ['get']
    model = models.Workflow
    ordering = ['name']
    wf_pf_related = ['shared', 'workflows_star', 'actions']

    def setup(self, request, *args, **kwargs):
        """Remove workflow from session and check celery if superuser."""
        super().setup(request, *args, **kwargs)

        # Remove the workflow from the session
        remove_workflow_from_session(request)

        # Report if Celery is not running properly
        if request.user.is_superuser:
            # Verify that celery is running!
            if not celery_is_up():
                messages.error(
                    request,
                    _(
                        'WARNING: Celery is not currently running. '
                        + 'Please configure it correctly.'))

    def get_queryset(self):
        """Return the list of workflows available for the user."""

        return super().get_queryset().filter(
            Q(user=self.request.user)
            | Q(shared=self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        """Get additional workflow fields in the context"""
        context = super().get_context_data(**kwargs)
        context['n_star_wflows'] = self.object_list.filter(
            star__in=[self.request.user]).count()
        return context


@method_decorator(ajax_required, name='dispatch')
class WorkflowCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    generic.CreateView
):
    """View to create a workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_form_kwargs(self):
        """Add the user in the request to the context."""
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        return services.log_workflow_createupdate(
            self.request,
            self.object,
            models.Log.WORKFLOW_CREATE)


@method_decorator(ajax_required, name='dispatch')
class WorkflowUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.UpdateView
):
    """View to update name or description of a workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.WorkflowForm
    template_name = 'workflow/includes/partial_workflow_update.html'

    def get_object(self, queryset=None):
        return self.workflow

    def get_form_kwargs(self):
        """Add the user in the request to the context."""
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Process the update operation"""
        if not form.has_changed() or not self.object:
            return http.JsonResponse({'html_redirect': ''})

        # Save object
        self.object = form.save()

        return services.log_workflow_createupdate(
            self.request,
            self.object,
            models.Log.WORKFLOW_UPDATE)


@method_decorator(ajax_required, name='dispatch')
class WorkflowCloneView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.TemplateView,
):
    """View to clone a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_workflow_clone.html'

    def post(self, request, *args, **kwargs):
        """Perform the clone operation."""
        try:
            services.do_clone_workflow(request.user, self.workflow)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()
        else:
            messages.success(request, _('Workflow successfully cloned.'))

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class WorkflowDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.DeleteView
):
    """View to delete a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_workflow_delete.html'

    def get_object(self, queryset=None):
        return self.workflow

    def delete(self, request, *args, **kwargs) -> http.JsonResponse:
        """Delete the workflow and log the event"""
        self.workflow.log(request.user, models.Log.WORKFLOW_DELETE)
        self.workflow.delete()
        return http.JsonResponse({'html_redirect': reverse('home')})
