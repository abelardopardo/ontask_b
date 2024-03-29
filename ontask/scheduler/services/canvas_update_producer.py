"""Service functions to handle Canvas course uploads."""

from django import http
from django.utils.translation import gettext

from ontask import models
from ontask.core import canvas_ops, session_ops
from ontask.scheduler import forms
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)


class ScheduledOperationUpdateCanvasUpload(ScheduledOperationUpdateBaseView):
    """Class to create a Canvas Upload operation."""

    operation_type = None
    form_page_title = None
    form_class = forms.ScheduleUploadCanvasForm

    def _create_payload(
        self,
        request: http.HttpRequest,
        **kwargs
    ) -> dict:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param kwargs: Dictionary with extra parameters
        :return: Dictionary with pairs name/value
        """
        payload = super()._create_payload(request, **kwargs)

        payload.update({
            'workflow_id': self.workflow.id,
            'page_title': gettext('Canvas Course Upload')})

        if self.object:
            payload['target_url'] = self.object.payload['target_url']
        else:
            payload['target_url'] = None

        return payload

    def form_valid(self, form) -> http.HttpResponse:
        """Process the valid POST request and insert Canvas Auth."""
        # Check for the CANVAS token and proceed to the continue_url
        session_ops.set_payload(self.request, self.op_payload)

        return canvas_ops.set_oauth_token(
            self.request,
            self.op_payload['target_url'],
            'scheduler:finish_scheduling',
            'scheduler:index')
