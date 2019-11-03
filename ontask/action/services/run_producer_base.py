# -*- coding: utf-8 -*-

"""Base class for the Action Run Producer"""

from typing import Any, Dict

from django import http
from django.shortcuts import render, redirect
from django.utils.translation import ugettext

from ontask import models, tasks
from ontask.action import payloads


class ActionRunServiceBase(object):
    """Base class to provide the service for the run views."""

    def __init__(self, form_class: Any, payload_class: Any):
        """Assign and initialize the main service parameters."""
        self.form_class = form_class
        self.payload_class = payload_class
        self.info_initial = None
        self.template = None
        self.log_event = None
        self.run_task = None

    def process_request(
        self,
        request: http.HttpRequest,
        action: models.Action,
    ) -> http.HttpResponse:
        action_info = None
        if self.payload_class:
            action_info = payloads.get_or_set_action_info(
                request.session,
                self.payload_class,
                action=action)

        form = self.form_class(
            request.POST or None,
            columns=action.workflow.columns.filter(is_key=True),
            action=action,
            form_info=action_info)

        if request.method == 'POST' and form.is_valid():
            return self.process_post(request, action, action_info)

        # Render the form
        return render(
            request,
            self.template,
            {'action': action,
             'num_msgs': action.get_rows_selected(),
             'form': form,
             'valuerange': range(2)})

    def process_post(
        self,
        request: http.HttpRequest,
        action: models.Action,
        action_info: Dict,
    ):
        if action_info['confirm_items']:
            # Add information to the session object to execute the next pages
            action_info['button_label'] = ugettext('Send')
            action_info['valuerange'] = 2
            action_info['step'] = 2
            payloads.set_action_payload(
                request.session,
                action_info.get_store())

            return redirect('action:item_filter')

        # Go straight to the final step.
        return self.process_done(
            request,
            action_info=action_info,
            workflow=action.workflow)

    def process_done(
        self,
        request: http.HttpRequest,
        action_info: Dict,
        workflow: models.Workflow,
    ):
        # Get the information from the payload
        action = workflow.actions.filter(pk=action_info['action_id']).first()
        if not action:
            return redirect('home')

        log_item = action.log(request.user, self.log_event, **action_info)

        tasks.run.delay(
            request.user.id,
            log_item.id,
            action_info.get_store())

        # Reset object to carry action info throughout dialogs
        payloads.set_action_payload(request.session)
        request.session.save()

        # Successful processing.
        return render(
            request,
            'action/action_done.html',
            {'log_id': log_item.id, 'download': action_info['export_wf']})
