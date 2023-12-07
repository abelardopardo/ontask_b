"""Functions to save the different types of scheduled actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _

from ontask import models
from ontask.core import SessionPayload
from ontask.core import canvas_ops
from ontask.scheduler.forms import (
    ScheduleEmailForm, ScheduleJSONForm, ScheduleJSONReportForm,
    ScheduleSendListForm, ScheduleCanvasEmailForm)
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)
from ontask.scheduler.services.items import create_timedelta_string


class ScheduledOperationActionRunUpdateView(ScheduledOperationUpdateBaseView):
    """Base class for those saving Action Run operations."""

    def _create_payload(
        self,
        request: http.HttpRequest,
        **kwargs
    ) -> SessionPayload:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param action: Corresponding action for the schedule operation type, or
        if empty, it is contained in the scheduled_item (Optional)
        :return: Dictionary with pairs name: value
        """
        if self.scheduled_item:
            exclude_values = self.scheduled_item.payload.get(
                'exclude_values',
                [])
        else:
            exclude_values = []

        # Get the payload from the session, and if not, use the given one
        payload = SessionPayload(
            request.session,
            initial_values={
                'action_id': self.action.id if self.action else None,
                'exclude_values': exclude_values,
                'operation_type': self.operation_type,
                'value_range': list(range(2)),
                'prev_url': request.path_info,
                'post_url': reverse('scheduler:finish_scheduling'),
                'page_title': gettext('Schedule Action Execution'),
            })
        if self.scheduled_item:
            payload.update(self.scheduled_item.payload)
            payload['schedule_id'] = self.scheduled_item.id

        return payload

    def form_valid(self, form) -> http.HttpResponse:
        if self.op_payload.get('confirm_items'):
            # Update information to carry to the filtering stage
            self.op_payload['button_label'] = gettext('Schedule')
            self.op_payload['value_range'] = 2
            self.op_payload['step'] = 2
            self.op_payload.store_in_session(self.request.session)

            return redirect('action:item_filter')

        # Go straight to the final step
        return self.finish(self.request, self.op_payload)

    def finish(
        self,
        request: http.HttpRequest,
        payload: SessionPayload,
    ) -> Optional[http.HttpResponse]:
        """Finalize the creation of a scheduled operation.

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
                    return redirect('action:index')
        else:
            action = models.Action.objects.get(pk=payload.pop('action_id'))
            payload['workflow'] = action.workflow
            payload['action'] = action

        # Remove some parameters from the payload
        for key in [
            'button_label',
            'value_range',
            'step',
            'prev_url',
            'post_url',
            'confirm_items',
            'action_id',
            'page_title',
        ]:
            payload.pop(key, None)

        try:
            scheduled_item = self.create_or_update(
                request.user,
                payload.get_store(),
                self.scheduled_item)
        except Exception as exc:
            messages.error(
                request,
                str(_('Unable to create scheduled operation: {0}')).format(
                    str(exc)))
            return redirect('action:index')

        scheduled_item.log(models.Log.SCHEDULE_EDIT)

        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        # Successful processing.
        tdelta = create_timedelta_string(
            scheduled_item.execute_start,
            scheduled_item.frequency,
            scheduled_item.execute_until)
        return render(
            request,
            'scheduler/schedule_done.html',
            {'tdelta': tdelta, 's_item': scheduled_item})


class ScheduledOperationEmailUpdateView(ScheduledOperationActionRunUpdateView):
    """Process Personalised Email."""

    operation_type = models.Log.ACTION_RUN_PERSONALIZED_EMAIL
    form_class = ScheduleEmailForm


class ScheduledOperationCanvasEmailUpdateView(
    ScheduledOperationActionRunUpdateView
):
    """Process Canvas Email form."""

    operation_type = models.Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL
    form_class = ScheduleCanvasEmailForm

    def form_valid(self, form) -> http.HttpResponse:
        """Process the VALID POST request and insert Canvas Auth."""
        if self.op_payload.get('confirm_items'):
            # Add information to the session object to execute the next pages
            self.op_payload['button_label'] = gettext('Schedule')
            self.op_payload['value_range'] = 2
            self.op_payload['step'] = 2
            continue_url = 'action:item_filter'
        else:
            continue_url = 'scheduler:finish_scheduling'

        self.op_payload.store_in_session(self.request.session)

        # Check for the CANVAS token and proceed to the continue_url
        return canvas_ops.get_or_set_oauth_token(
            self.request,
            self.op_payload['target_url'],
            continue_url,
            'action:index')


class ScheduledOperationEmailReportUpdateView(
    ScheduledOperationActionRunUpdateView
):
    """Process Email Report."""

    operation_type = models.Log.ACTION_RUN_EMAIL_REPORT
    form_class = ScheduleSendListForm


class ScheduledOperationJSONUpdateView(ScheduledOperationActionRunUpdateView):
    """Process Personalised JSON."""

    operation_type = models.Log.ACTION_RUN_PERSONALIZED_JSON
    form_class = ScheduleJSONForm


class ScheduledOperationJSONReportUpdateView(
    ScheduledOperationActionRunUpdateView
):
    """Process JSON Report."""

    operation_type = models.Log.ACTION_RUN_JSON_REPORT
    form_class = ScheduleJSONReportForm
