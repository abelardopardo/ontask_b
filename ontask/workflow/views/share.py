# -*- coding: utf-8 -*-

"""Views to create and delete a "share" item for a workflow."""
from typing import Dict

from django import http
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.core import (
    JSONFormResponseMixin, WorkflowView, UserIsInstructor,
    ajax_required)
from ontask.workflow import forms


@method_decorator(ajax_required, name='dispatch')
class WorkflowShareCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.FormView,
):
    """View to create a new "share" user in the workflow."""

    http_method_names = ['get', 'post']
    form_class = forms.SharedForm
    template_name = 'workflow/includes/partial_share_create.html'

    def get_form_kwargs(self) -> Dict:
        """Store workflow and request.user in kwargs"""
        form_kwargs = super().get_form_kwargs()
        form_kwargs['workflow'] = self.workflow
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def form_valid(self, form) -> http.JsonResponse:
        """Store the new shared user"""
        self.workflow.shared.add(form.user_obj)
        self.workflow.save()
        self.workflow.log(
            self.request.user,
            models.Log.WORKFLOW_SHARE_ADD,
            share_email=form.user_obj.email)
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class WorkflowShareDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.TemplateView,
):
    """View to delete a "share" user in the workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_share_delete.html'

    def get_context_data(self, **kwargs):
        """Add pk and user email to the context."""
        context = super().get_context_data(**kwargs)
        user = get_user_model().objects.filter(id=kwargs['pk']).first()
        if not user:
            raise http.Http404(_('Unable to find user'))
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        """Perform the share delete operation."""
        user = get_user_model().objects.filter(id=kwargs['pk']).first()
        if not user:
            raise http.Http404(_('Unable to find user'))
        self.workflow.shared.remove(user)
        self.workflow.save()
        self.workflow.log(
            request.user,
            models.Log.WORKFLOW_SHARE_DELETE,
            share_email=user.email)

        return http.JsonResponse({'html_redirect': ''})
