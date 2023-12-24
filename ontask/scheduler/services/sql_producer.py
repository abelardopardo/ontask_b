"""Service to create a SQL update operation."""
from typing import Optional

from django import http
from django.utils.translation import gettext

import ontask.scheduler.forms.basic
from ontask import models
from ontask.core import session_ops
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)


class ScheduledOperationUpdateSQLUpload(ScheduledOperationUpdateBaseView):
    """Class to create a SQL Upload operation."""

    operation_type = models.Log.WORKFLOW_DATA_SQL_UPLOAD
    form_class = ontask.scheduler.forms.basic.ScheduleSQLUploadForm

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
        # Get the payload from the session, and if not, use the given one
        payload = {
            'workflow_id': self.workflow.id,
            'operation_type': self.operation_type,
            'value_range': [],
            'page_title': gettext('Schedule SQL Upload')}
        session_ops.set_payload(request, payload)

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
