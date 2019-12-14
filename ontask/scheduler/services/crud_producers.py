# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""
from datetime import datetime

from django import http
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext, ugettext_lazy as _
import pytz

from ontask import models
from ontask.core import SessionPayload
from ontask.scheduler import forms, services


class ScheduledOperationSaveBase:
    """Base class for all the scheduled operation save producers.

    :Attribute operation_type: The value to store in the scheduled item
    and needs to be overwritten by subclasses

    :Attribute form_class: Form to be used when creating one operation in the
    Web interface.
    """

    operation_type = None
    form_class = None

    def process(
        self,
        request: http.HttpRequest,
        action: models.Action,
        schedule_item: models.ScheduledOperation,
        prev_url: str,
    ) -> http.HttpResponse:
        """Process the request."""
        op_payload = services.create_payload(
            request,
            self.operation_type,
            prev_url,
            schedule_item,
            action)

        form = self.form_class(
            form_data=request.POST or None,
            action=action,
            instance=schedule_item,
            columns=action.workflow.columns.filter(is_key=True),
            form_info=op_payload)
        if request.method == 'POST' and form.is_valid():
            return self.process_post(request, schedule_item, op_payload)

        frequency = op_payload.get('frequency')
        if not frequency:
            frequency = '0 5 * * 0'

        return render(
            request,
            'scheduler/edit.html',
            {
                'action': action,
                'form': form,
                'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
                'frequency': frequency,
                'valuerange': range(2),
            },
        )

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ):
        """Process a POST request."""
        del request, schedule_item, op_payload
        raise ValueError('Incorrect  invocation of process_post method')

    @staticmethod
    def finish(
        request: http.HttpRequest,
        payload: SessionPayload,
        schedule_item: models.ScheduledOperation = None,
    ) -> http.HttpResponse:
        """Finalize the creation of a scheduled operation.

        All required data is passed through the payload.

        :param request: Request object received
        :param schedule_item: ScheduledOperation item being processed. If None,
        it has to be extracted from the information in the payload.
        :param payload: Dictionary with all the required data coming from
        previous requests.
        :return: Http Response
        """
        # Get the scheduled operation
        s_item_id = payload.pop('schedule_id', None)
        action = models.Action.objects.get(pk=payload.pop('action_id'))
        column_pk = payload.pop('item_column', None)
        column = None
        if column_pk:
            column = action.workflow.columns.filter(pk=column_pk).first()

        # Remove some parameters from the payload
        for key in [
            'button_label',
            'valuerange',
            'step',
            'prev_url',
            'post_url',
            'confirm_items',
        ]:
            payload.pop(key, None)
        operation_type = payload.pop('operation_type')

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
            schedule_item = models.ScheduledOperation(
                user=request.user,
                workflow=action.workflow,
                action=action,
                operation_type=operation_type)

        # Update the other fields
        schedule_item.name = payload.pop('name')
        schedule_item.description_text = payload.pop('description_text')
        schedule_item.item_column = column
        schedule_item.execute = parse_datetime(payload.pop('execute'))
        schedule_item.frequency = payload.pop('frequency')
        schedule_item.execute_until = parse_datetime(
            payload.pop('execute_until'))
        schedule_item.exclude_values = payload.pop('exclude_values', [])
        schedule_item.status = models.scheduler.STATUS_PENDING
        schedule_item.payload = payload.get_store()

        # Save and log
        schedule_item.save()
        schedule_item.log(models.Log.SCHEDULE_EDIT)

        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        # Successful processing.
        tdelta = services.create_timedelta_string(
            schedule_item.execute,
            schedule_item.frequency,
            schedule_item.execute_until)
        return render(
            request,
            'scheduler/schedule_done.html',
            {'tdelta': tdelta, 's_item': schedule_item})


class ScheduledOperationSaveActionRun(ScheduledOperationSaveBase):
    """Base class for those saving Action Run operations."""

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


