# -*- coding: utf-8 -*-

"""Views to render the list of actions."""
from typing import Optional, Union, List

from django import http
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import create_new_name, models
from ontask.action import forms, services
from ontask.core import (
    SessionPayload, UserIsInstructor, ajax_required, JSONFormResponseMixin,
    WorkflowView, ActionView, SingleActionMixin)


class ActionIndexView(UserIsInstructor, WorkflowView, generic.ListView):
    """View to list actions in a workflow."""

    http_method_names = ['get']
    model = models.Action
    ordering = ['name']

    def get_queryset(self):
        """Return the actions for the workshop in the view"""
        return self.workflow.actions.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'action_types': models.Action.AVAILABLE_ACTION_TYPES})
        return context

    def get(self, request, *args, **kwargs):
        SessionPayload.flush(request.session)
        return super().get(request, *args, **kwargs)


@method_decorator(ajax_required, name='dispatch')
class ActionCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.CreateView
):
    """Process get/post requests to create an action."""

    http_method_names = ['get', 'post']
    form_class = forms.ActionForm
    template_name = 'action/includes/partial_action_create.html'

    def get_form_kwargs(self):
        """Add the user in the request to the context."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def get_context_data(self, **kwargs):
        """Get context data: fid as filter ID (optional)"""
        context = super().get_context_data(**kwargs)
        fid = self.kwargs.get('fid')
        if fid is None:
            context['form_url'] = reverse('action:create')
        else:
            context['form_url'] = reverse(
                'action:create_from_view',
                kwargs={'fid': fid})
        return context

    def form_valid(self, form):
        """Process a valid post to create the action."""
        return_url = None

        if form.instance.id:
            log_type = models.Log.ACTION_UPDATE
            return_url = reverse('action:index')
        else:
            log_type = models.Log.ACTION_CREATE

        action = form.save()
        if not return_url:
            return_url = reverse('action:edit', kwargs={'pk': action.id})

        return services.save_action_form(
            action,
            self.request.user,
            log_type,
            return_url,
            self.kwargs.get('fid'))


@method_decorator(ajax_required, name='dispatch')
class ActionUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleActionMixin,
    ActionView,
    generic.UpdateView
):
    """Process the Action Update view."""

    http_method_names = ['get', 'post']
    form_class = forms.ActionUpdateForm
    template_name = 'action/includes/partial_action_update.html'

    def get_form_kwargs(self):
        """Add the user in the request to the context."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        """Process a valid post to create the action."""
        return services.save_action_form(
            form.save(),
            self.request.user,
            models.Log.ACTION_UPDATE,
            reverse('action:index'))


@method_decorator(ajax_required, name='dispatch')
class ActionDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleActionMixin,
    ActionView,
    generic.DeleteView
):
    """View to delete an action."""

    http_method_names = ['get', 'post']
    template_name = 'action/includes/partial_action_delete.html'

    def delete(self, request, *args, **kwargs):
        action = self.get_object()
        action.log(request.user, models.Log.ACTION_DELETE)
        action.delete()
        return http.JsonResponse({'html_redirect': reverse('action:index')})


class ActionEditView(UserIsInstructor, ActionView):
    """View to edit an action."""

    http_method_names = ['get', 'post']
    pf_related: Optional[Union[str, List]] = ['actions', 'columns']

    def get(self, request, *args, **kwargs):
        return services.ACTION_PROCESS_FACTORY.process_edit_request(
            self.request,
            self.action)

    def post(self, request, *args, **kwargs):
        return services.ACTION_PROCESS_FACTORY.process_edit_request(
            self.request,
            self.action)


@method_decorator(ajax_required, name='dispatch')
class ActionCloneView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.TemplateView
):
    """Process the Action Update view."""

    http_method_names = ['get', 'post']
    template_name = 'action/includes/partial_action_clone.html'
    pf_related = 'actions'

    def post(self, request, *args, **kwargs):
        """Perform the clone operation."""
        self.action = self.get_object()
        services.do_clone_action(
            self.request.user,
            self.action,
            new_workflow=None,
            new_name=create_new_name(self.action.name, self.workflow.actions))

        messages.success(request, _('Action successfully cloned.'))
        return http.JsonResponse({'html_redirect': ''})
