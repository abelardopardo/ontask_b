"""Service to create a SQL update operation.."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext, gettext_lazy as _

from ontask import models
from ontask.core import SessionPayload
from ontask.scheduler import forms
from ontask.scheduler.services.crud_factory import ScheduledOperationUpdateBase
from ontask.scheduler.services.items import create_timedelta_string


class ScheduledOperationUpdateSQLUpload(ScheduledOperationUpdateBase):
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
                'valuerange': [],
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

    def finish(
        self,
        request: http.HttpRequest,
        payload: SessionPayload,
    ) -> Optional[http.HttpResponse]:
        """Finalize the creation of a SQL upload operation.

        All required data is passed through the payload.

        :param request: Request object received
        it has to be extracted from the information in the payload.
        :param payload: Dictionary with all the required data coming from
        previous requests.
        :return: Http Response
        """
        s_item_id = payload.pop('schedule_id', None)
        if s_item_id:
            # Get the item being processed
            if not self.scheduled_item:
                self.scheduled_item = models.ScheduledOperation.objects.filter(
                    id=s_item_id).first()
            if not self.scheduled_item:
                messages.error(
                    request,
                    _('Incorrect request for operation scheduling'))
                return redirect('scheduler:index')
        else:
            payload['workflow'] = models.Workflow.objects.get(
                pk=payload.pop('workflow_id'))

        # Remove some parameters from the payload
        for key in ['valuerange', 'workflow_id', 'page_title']:
            payload.pop(key, None)

        try:
            schedule_item = self.create_or_update(
                request.user,
                payload.get_store(),
                self.scheduled_item)
        except Exception as exc:
            messages.error(
                request,
                str(_('Unable to create scheduled operation ({0})')).format(
                    str(exc)))
            return redirect('scheduler:index')

        schedule_item.log(models.Log.SCHEDULE_EDIT)

        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        # Successful processing.
        tdelta = create_timedelta_string(
            schedule_item.execute,
            schedule_item.frequency,
            schedule_item.execute_until)
        return render(
            request,
            'scheduler/schedule_done.html',
            {'tdelta': tdelta, 's_item': schedule_item})
