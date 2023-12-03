"""Service to create a SQL update operation.."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext, gettext_lazy as _

from ontask import models
from ontask.core import SessionPayload
from ontask.scheduler import forms
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)
from ontask.scheduler.services.items import create_timedelta_string


class ScheduledOperationUpdateSQLUpload(ScheduledOperationUpdateBaseView):
    """Base class for those saving SQL Upload operations."""

    operation_type = models.Log.WORKFLOW_DATA_SQL_UPLOAD
    form_class = forms.ScheduleSQLUploadForm

    def _create_payload(
        self,
        request: http.HttpRequest,
        **kwargs
    ) -> SessionPayload:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param kwargs: Dictionary with extra parameters
        :return: Dictionary with pairs name/value
        """
        # Get the payload from the session, and if not, use the given one
        payload = SessionPayload(
            request.session,
            initial_values={
                'workflow_id': self.workflow.id,
                'operation_type': self.operation_type,
                'value_range': [],
                'page_title': gettext('Schedule SQL Upload')})

        if self.scheduled_item:
            payload.update(self.scheduled_item.payload)
            payload['schedule_id'] = self.scheduled_item.id
            payload['connection_id'] = self.scheduled_item.payload[
                'connection_id']
        else:
            payload['connection_id'] = self.connection.id

        return payload

    def form_valid(self, form) -> http.HttpResponse:
        """Process the valid form."""
        # Go straight to the final step
        return self.finish(self.request, self.op_payload)
