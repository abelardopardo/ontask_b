# -*- coding: utf-8 -*-

"""Base class for CRUD manager for actions."""
from typing import Dict, Optional

from django import http
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext

from ontask import models, tasks
from ontask.core import SessionPayload


class ActionRunManager:
    """Base class to provide the service for the run views."""

    def _create_log_event(
        self,
        user,
        action: models.Action,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        if log_item or not self.log_event:
            return log_item

        log_payload = dict(payload)
        log_payload['operation_type'] = self.log_event
        return action.log(user, **log_payload)

    def __init__(self, *args, **kwargs):
        """Assign and initialize the main service parameters."""
        self.run_form_class = kwargs.pop('run_form_class', None)
        self.run_template = kwargs.pop('run_template', None)
        self.log_event = kwargs.pop('log_event', None)
        super().__init__(*args, **kwargs)

    def process_run_request(
        self,
        operation_type: str,
        request: http.HttpRequest,
        action: models.Action,
        prev_url: str,
    ) -> http.HttpResponse:
        """Process a request (GET or POST)."""
        payload = SessionPayload(
            request.session,
            initial_values={
                'action_id': action.id,
                'operation_type': operation_type,
                'prev_url': prev_url,
                'post_url': reverse('action:run_done')})

        form = self.run_form_class(
            request.POST or None,
            columns=action.workflow.columns.filter(is_key=True),
            action=action,
            form_info=payload)

        if request.method == 'POST' and form.is_valid():
            return self.process_run_post(request, action, payload)

        # Render the form
        return render(
            request,
            self.run_template,
            {'action': action,
             'num_msgs': action.get_rows_selected(),
             'form': form,
             'valuerange': range(2)})

    def process_run_post(
        self,
        request: http.HttpRequest,
        action: models.Action,
        payload: SessionPayload,
    ) -> http.HttpResponse:
        """Process the VALID POST request."""
        if payload.get('confirm_items'):
            # Add information to the session object to execute the next pages
            payload['button_label'] = ugettext('Send')
            payload['valuerange'] = 2
            payload['step'] = 2
            payload.store_in_session(request.session)

            return redirect('action:item_filter')

        # Go straight to the final step.
        return self.process_run_request_done(
            request,
            workflow=action.workflow,
            payload=payload,
            action=action)

    def process_run_request_done(
        self,
        request: http.HttpRequest,
        workflow: models.Workflow,
        payload: SessionPayload,
        action: Optional[models.Action] = None,
    ):
        """Finish processing the request after item selection."""
        # Get the information from the payload
        if not action:
            action = workflow.actions.filter(pk=payload['action_id']).first()
            if not action:
                return redirect('home')

        log_item = self._create_log_event(
            request.user,
            action,
            payload.get_store())

        tasks.execute_operation.delay(
            action.action_type,
            user_id=request.user.id,
            log_id=log_item.id,
            workflow_id=workflow.id,
            action_id=action.id if action else None,
            payload=payload.get_store())

        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        # Successful processing.
        return render(
            request,
            'action/run_done.html',
            {'log_id': log_item.id, 'download': payload['export_wf']})

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Run the action."""
        raise Exception('Incorrect invocation of run method.')
