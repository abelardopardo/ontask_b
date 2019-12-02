# -*- coding: utf-8 -*-

"""Forms for scheduling actions."""
import datetime
from typing import Dict

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _
import pytz

from ontask import models
from ontask.action import forms as action_forms
from ontask.core import forms as ontask_forms


class ScheduleBasicForm(ontask_forms.FormWithPayload, forms.ModelForm):
    """Form to create/edit objects of the ScheduleAction.

    To be used for the various types of actions.
    """

    def __init__(self, form_data, *args, **kwargs):
        """Set item_column values."""
        super().__init__(form_data, *args, **kwargs)

        self.set_fields_from_dict(['name', 'description_text'])
        self.fields['execute'].initial = parse_datetime(
            self.get_payload_field('execute', ''))
        self.fields['execute_until'].initial = parse_datetime(
            self.get_payload_field('execute_until', ''))

    def clean(self) -> Dict:
        """Verify that the date is corre    ct."""
        form_data = super().clean()

        self.store_fields_in_dict([
            ('name', None),
            ('description_text', None),
            ('execute', str(form_data['execute'])),
            ('execute_until', str(form_data['execute_until']))])

        # The executed time must be in the future
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        when_data = self.cleaned_data.get('execute')
        until_data = self.cleaned_data.get('execute_until')
        if when_data and not until_data and when_data <= now:
            self.add_error(
                'execute',
                _('Date/time must be in the future'))

        if until_data:
            if until_data <= when_data:
                self.add_error(
                    'execute_until',
                    _('Final execution date/time must be after '
                      + 'the previous one'))
            elif until_data <= now:
                self.add_error(
                    'execute_until',
                    _('Final execution date/time must be in the future'))

        return form_data

    class Meta:
        """Define model, fields and widgets."""

        model = models.ScheduledOperation
        fields = ('name', 'description_text', 'execute', 'execute_until')
        widgets = {
            'execute': DateTimePickerInput(
                options=ontask_forms.DATE_TIME_WIDGET_OPTIONS),
            'execute_until':
                DateTimePickerInput(
                    options=ontask_forms.DATE_TIME_WIDGET_OPTIONS)}


class ScheduleEmailForm(ScheduleBasicForm, action_forms.EmailActionForm):
    """Form to create/edit objects of the ScheduleAction of type email.

    One of the fields is a reference to a key column, which is a subset of
    the columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

    def __init__(self, form_data, *args, **kwargs):
        """Set field order."""
        super().__init__(form_data, *args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute',
            'execute_until',
            'item_column',
            'subject',
            'cc_email',
            'bcc_email',
            'confirm_items',
            'send_confirmation',
            'track_read'])


class ScheduleSendListForm(ScheduleBasicForm, action_forms.SendListActionForm):
    """Form to create/edit objects of the ScheduleAction of type send list."""

    def __init__(self, form_data, *args, **kwargs):
        """Set field order."""
        super().__init__(form_data, *args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute',
            'execute_until',
            'email_to',
            'subject',
            'cc_email',
            'bcc_email'])


class ScheduleJSONForm(ScheduleBasicForm, action_forms.JSONActionForm):
    """Form to edit ScheduleAction of type JSON."""

    def __init__(self, form_data, *args, **kwargs):
        """Set field order."""
        super().__init__(form_data, *args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute',
            'execute_until',
            'item_column',
            'confirm_items',
            'token'])


class ScheduleJSONListForm(ScheduleBasicForm, action_forms.JSONListActionForm):
    """Form to edit ScheduleAction of types JSON List."""

    def __init__(self, form_data, *args, **kwargs):
        """Set field order."""
        super().__init__(form_data, *args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute',
            'execute_until',
            'token'])


class ScheduleCanvasEmailForm(
    ScheduleBasicForm,
    action_forms.CanvasEmailActionForm,
):
    """Form to schedule Action of type canvas email."""

    def __init__(self, form_data, *args, **kwargs):
        """Set field order."""
        super().__init__(form_data, *args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'subject',
            'execute',
            'execute_until'])
