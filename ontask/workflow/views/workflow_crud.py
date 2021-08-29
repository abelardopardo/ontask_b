# -*- coding: utf-8 -*-

"""Views implementing CRUD operations with workflows."""

from django import http
from django.contrib import messages
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.celery import celery_is_up
from ontask.core import (
    JSONFormResponseMixin, SingleWorkflowMixin,
    UserIsInstructor, ajax_required, remove_workflow_from_session)
from ontask.workflow import forms, services


class WorkflowIndexView(UserIsInstructor, generic.ListView):
    """View to list user workflows."""

    http_method_names = ['get']
    model = models.Workflow
    ordering = ['name']

    def setup(self, request, *args, **kwargs):
        """Perform two operations before rendering the page"""

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
                        + 'Please configure it correctly.',
                    ),
                )

    def get_queryset(self):
        """Return the list of workflows available for the user."""

        return super().get_queryset().filter(
            Q(user=self.request.user)
            | Q(shared=self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        """Get additional workflow fields in the context"""
        kwargs = super().get_context_data(**kwargs)
        kwargs['n_star_wflows'] = self.object_list.filter(
            star__in=[self.request.user]).count()

        return kwargs


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
    SingleWorkflowMixin,
    JSONFormResponseMixin,
    generic.UpdateView
):
    """View to update name or description of a workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.WorkflowForm
    template_name = 'workflow/includes/partial_workflow_update.html'

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
        super().form_valid(form)

        return services.log_workflow_createupdate(
            self.request,
            self.object,
            models.Log.WORKFLOW_UPDATE)


@method_decorator(ajax_required, name='dispatch')
class WorkflowDeleteView(
    UserIsInstructor,
    SingleWorkflowMixin,
    JSONFormResponseMixin,
    generic.DeleteView
):
    """View to delete a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_workflow_delete.html'

    def delete(self, request, *args, **kwargs):
        """Delete the workflow and log the event"""

        self.object = self.get_object()

        models.Log.objects.register(
            request.user,
            models.Log.WORKFLOW_DELETE,
            self.object,
            {
                'name': self.object.name,
                'ncols': self.object.ncols,
                'nrows': self.object.nrows})

        self.object.delete()

        return http.JsonResponse({'html_redirect': reverse('home')})


@method_decorator(ajax_required, name='dispatch')
class WorkflowCloneView(
    UserIsInstructor,
    SingleWorkflowMixin,
    JSONFormResponseMixin,
    generic.DetailView,
):
    """View to clone a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_workflow_clone.html'

    def post(self, request, *args, **kwargs):
        """Perform the clone operation."""

        try:
            services.do_clone_workflow(self.request.user, self.get_object())
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()
        else:
            messages.success(
                self.request,
                _('Workflow successfully cloned.'))

        return http.JsonResponse({'html_redirect': ''})
