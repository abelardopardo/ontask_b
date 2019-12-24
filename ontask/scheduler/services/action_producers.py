# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask import models
from ontask.core import SessionPayload
from ontask.scheduler import forms
from ontask.scheduler.services.crud_factory import ScheduledOperationSaveBase
from ontask.scheduler.services.items import create_timedelta_string


class ScheduledOperationSaveActionRun(ScheduledOperationSaveBase):
    """Base class for those saving Action Run operations."""

    def _create_payload(self, **kwargs) -> SessionPayload:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param operation_type: String denoting the type of s_item being
        processed
        :param s_item: Existing schedule item being processed (Optional)
        :param prev_url: String with the URL to use to "go back"
        :param action: Corresponding action for the schedule operation type, or
        if empty, it is contained in the scheduled_item (Optional)
        :return: Dictionary with pairs name: value
        """
        s_item = kwargs.get('schedule_item')
        action = kwargs.get('action')
        if s_item:
            action = s_item.action
            exclude_values = s_item.exclude_values
        else:
            exclude_values = []

        # Get the payload from the session, and if not, use the given one
        payload = SessionPayload(
            kwargs.get('request').session,
            initial_values={
                'action_id': action.id,
                'exclude_values': exclude_values,
                'operation_type': self.operation_type,
                'valuerange': list(range(2)),
                'prev_url': kwargs.get('prev_url'),
                'post_url': reverse('scheduler:finish_scheduling'),
                'page_title': ugettext('Schedule Action Execution'),
            })
        if s_item:
            payload.update(s_item.payload)
            payload['schedule_id'] = s_item.id
            if s_item.item_column:
                payload['item_column'] = s_item.item_column.pk

        return payload

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ) -> http.HttpResponse:
        """Process the valid form."""
        if op_payload.get('confirm_items'):
            # Update information to carry to the filtering stage
            op_payload['button_label'] = ugettext('Schedule')
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            op_payload.store_in_session(request.session)

            return redirect('action:item_filter')

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
        schedule_item = None
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
            action = models.Action.objects.get(pk=payload.pop('action_id'))
            payload['workflow'] = action.workflow
            payload['action'] = action

        # Remove some parameters from the payload
        for key in [
            'button_label',
            'valuerange',
            'step',
            'prev_url',
            'post_url',
            'confirm_items',
            'action_id',
            'page_title',
        ]:
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
            return redirect('action:index')

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


class ScheduledOperationSaveEmail(ScheduledOperationSaveActionRun):
    """Process Personalised Email."""

    operation_type = models.Log.ACTION_RUN_PERSONALIZED_EMAIL
    form_class = forms.ScheduleEmailForm


class ScheduledOperationSaveEmailList(ScheduledOperationSaveActionRun):
    """Process Email List."""

    operation_type = models.Log.ACTION_RUN_EMAIL_LIST
    form_class = forms.ScheduleSendListForm


class ScheduledOperationSaveJSON(ScheduledOperationSaveActionRun):
    """Process Personalised JSON."""

    operation_type = models.Log.ACTION_RUN_PERSONALIZED_JSON
    form_class = forms.ScheduleJSONForm


class ScheduledOperationSaveJSONList(ScheduledOperationSaveActionRun):
    """Process JSON List."""

    operation_type = models.Log.ACTION_RUN_JSON_LIST
    form_class = forms.ScheduleJSONListForm
