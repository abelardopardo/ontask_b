# -*- coding: utf-8 -*-

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
    """Base class for those saving Action Run operations."""

    operation_type = models.Log.WORKFLOW_DATA_SQL_UPLOAD
    form_class = forms.ScheduleSQLUploadForm

    def _create_payload(self, **kwargs) -> SessionPayload:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param operation_type: String denoting the type of s_item being
        processed
        :param s_item: Existing schedule item being processed (Optional)
        :return: Dictionary with pairs name/value
        """

        # Get the payload from the session, and if not, use the given one
        payload = SessionPayload(
            kwargs.get('request').session,
            initial_values={
                'workflow_id': kwargs.get('workflow').id,
                'operation_type': self.operation_type,
                'valuerange': [],
                'page_title': gettext('Schedule SQL Upload')})

        s_item = kwargs.get('schedule_item')
        if s_item:
            payload.update(s_item.payload)
            payload['schedule_id'] = s_item.id
            payload['connection_id'] = s_item.payload['connection_id']
        else:
            payload['connection_id'] = kwargs.get('connection').id


        return payload

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ) -> http.HttpResponse:
        """Process the valid form."""
        # Go straight to the final step
        return self.finish(request, op_payload, schedule_item)

    def finish(
        self,
        request: http.HttpRequest,
        payload: SessionPayload,
        schedule_item: models.ScheduledOperation = None,
    ) -> Optional[http.HttpResponse]:
        """Finalize the creation of a scheduled operation.

        All required data is passed through the payload.

        :param request: Request object received
        :param schedule_item: ScheduledOperation item being processed. If None,
        it has to be extracted from the information in the payload.
        :param payload: Dictionary with all the required data coming from
        previous requests.
        :return: Http Response
        """
        s_item_id = payload.pop('schedule_id', None)
        if s_item_id:
            # Get the item being processed
            if not schedule_item:
                schedule_item = models.ScheduledOperation.objects.filter(
                    id=s_item_id).first()
            if not schedule_item:
                messages.error(
                    request,
                    _('Incorrect request for operation scheduling'))
                return redirect('action:index')
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
                schedule_item)
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
