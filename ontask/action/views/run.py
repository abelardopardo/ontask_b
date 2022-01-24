# -*- coding: utf-8 -*-

"""Views to run and serve actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.action import forms, services
from ontask.celery import celery_is_up
from ontask.core import (
    ActionView, DataTablesServerSidePaging, SessionPayload,
    UserIsInstructor, WorkflowView, ajax_required)


class ActionRunBasicView(UserIsInstructor):
    """Basic view to process a run request for an action."""

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        return self.post(request, *args, **kwargs)


class ActionRunView(ActionRunBasicView, ActionView):
    """Export the actions given as comma separated list of ids."""

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        if not celery_is_up():
            messages.error(
                request,
                _('Unable to execute actions due to a misconfiguration. '
                  + 'Ask your system administrator to enable message '
                    'queueing.'))
            return redirect(reverse('action:index'))

        action = self.get_object()
        reason = action.is_executable()
        if reason:
            messages.error(request,  reason)
            return redirect(reverse('action:index'))

        return services.ACTION_PROCESS_FACTORY.process_run_request(
            action.action_type,
            request=request,
            action=action,
            prev_url=reverse('action:run', kwargs={'pk': action.id}))


class ActionRunDoneView(ActionRunBasicView, WorkflowView):
    """Export the actions given as comma separated list of ids."""

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        payload = SessionPayload(request.session)
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(
                request,
                _('Incorrect action run invocation.'))
            return redirect('action:index')

        return services.ACTION_PROCESS_FACTORY.process_run_request_done(
            payload.get('operation_type'),
            request=request,
            workflow=self.workflow,
            payload=payload)


class ActionRunZipView(ActionRunBasicView, ActionView):
    """Request data to create a zip file."""

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        action = self.get_object()
        return services.ACTION_PROCESS_FACTORY.process_run_request(
            models.action.ZIP_OPERATION,
            request=request,
            action=action,
            prev_url=reverse(
                'action:zip_action',
                kwargs={'pk': action.id}))


class ActionRunActionItemFilterView(
    UserIsInstructor,
    WorkflowView,
    generic.FormView,
):
    """Offer a select widget to tick items to exclude from selection.

    This is a generic Web function. It assumes that the session object has a
    dictionary with a field stating what objects need to be considered for
    selection. It creates the right web form and then updates in the session
    dictionary the result and proceeds to a URL given also as part of that
    dictionary.
    """

    http_method_names = ['get', 'post']
    form_class = forms.ValueExcludeForm
    template_name = 'action/item_filter.html'

    payload = None
    action = None
    item_column = None

    def _extract_payload(self, request) -> Optional[http.HttpResponse]:
        """Verify that data in the payload is correct."""

        self.payload = SessionPayload(request.session)
        if self.payload is None:
            # Something is wrong. Return to the action table.
            messages.error(request, _('Incorrect item filter invocation.'))
            return redirect('action:index')

        # Get the information from the payload
        try:
            self.action = self.workflow.actions.get(
                pk=self.payload['action_id'])
            self.item_column = self.workflow.columns.get(
                pk=self.payload['item_column'])
        except Exception:
            # Something is wrong. Return to the action table.
            messages.error(request, _('Incorrect item filter invocation.'))
            return redirect('action:index')
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action': self.action,
            'button_label': self.payload['button_label'],
            'valuerange': range(self.payload['valuerange']),
            'step': self.payload['step'],
            'prev_step': self.payload['prev_url']})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'action': self.action,
            'column_name': self.item_column.name,
            'form_info': self.payload})
        return kwargs

    def get(self, request, *args, **kwargs):
        payload_status = self._extract_payload(request)
        if payload_status:
            return payload_status
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        payload_status = self._extract_payload(request)
        if payload_status:
            return payload_status
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        return redirect(self.payload['post_url'])


class ActionZipExportView(UserIsInstructor, WorkflowView):
    """Create a zip with the personalised text and return it as response."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        payload = SessionPayload(request.session)
        if not payload:
            # Something is wrong with this execution. Return to action table.
            messages.error(request, _('Incorrect ZIP action invocation.'))
            return redirect('action:index')

        # Payload has the right keys
        if any(
            key_name not in payload.keys()
            for key_name in [
                'action_id', 'zip_for_moodle', 'item_column',
                'user_fname_column',
                'file_suffix']):
            messages.error(
                request,
                _('Incorrect payload in ZIP action invocation'))
            return redirect('action:index')

        # Get the action
        action = self.workflow.actions.filter(pk=payload['action_id']).first()
        if not action:
            return redirect('home')

        item_column = self.workflow.columns.get(pk=payload['item_column'])
        if not item_column:
            messages.error(
                request,
                _('Incorrect payload in ZIP action invocation'))
            return redirect('action:index')

        user_fname_column = None
        if payload['user_fname_column']:
            user_fname_column = self.workflow.columns.get(
                pk=payload['user_fname_column'])

        # Create the ZIP with the eval data tuples and return it for download
        return services.create_and_send_zip(
            request.session,
            action,
            item_column,
            user_fname_column,
            payload)


@method_decorator(ajax_required, name='dispatch')
class ActionShowSurveyTableSSView(UserIsInstructor, ActionView):
    """Process the server-side to show the survey table."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        # Check that the POST parameters are correctly given
        dt_page = DataTablesServerSidePaging(request)
        if not dt_page.is_valid:
            return http.JsonResponse(
                {'error': _('Incorrect request. Unable to process')})

        return services.create_survey_table(
            self.workflow,
            action,
            dt_page)
