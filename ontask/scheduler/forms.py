# -*- coding: utf-8 -*-

"""Forms for scheduling actions."""

import datetime
from builtins import object

import pytz
from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ontask import is_correct_email
from ontask.core.forms import date_time_widget_options
from ontask.dataops.sql.row_queries import get_rows
from ontask.models import Column, ScheduledAction


class ScheduleBasicForm(forms.ModelForm):
    """Form to create/edit objects of the ScheduleAction.

    To be used for the various types of actions.
    """
    action = None

    def __init__(self, form_data, *args, **kwargs):
        """Set item_column values."""
        self.action = kwargs.pop('action')

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

    def clean(self):
        """Verify that the date is correct."""
        form_data = super().clean()

        # The executed time must be in the future
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        when_data = self.cleaned_data.get('execute')
        if when_data and when_data <= now:
            self.add_error(
                'execute',
                _('Date/time must be in the future'))

        return form_data

    class Meta(object):
        """Define model, fields and widgets."""

        model = ScheduledAction
        fields = ('name', 'description_text', 'execute')
        widgets = {
            'execute': DateTimePickerInput(options=date_time_widget_options),
        }


class ScheduleMailSubjectForm(forms.Form):
    subject = forms.CharField(
        initial='',
        label=_('Email subject'),
        strip=True,
        required=True)

    def __init__(self, form_data, *args, **kwargs):
        """Set subject value."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        if self.instance:
            payload = self.instance.payload
            self.fields['subject'].initial = payload.get('subject')


class ScheduleMailCCForm(forms.Form):
    cc_email = forms.CharField(
        initial='',
        label=_('Comma-separated list of CC Emails'),
        strip=True,
        required=False)

    bcc_email = forms.CharField(
        initial='',
        label=_('Comma-separated list of BCC Emails'),
        strip=True,
        required=False)

    instance = None

    def __init__(self, form_data, *args, **kwargs):
        """Set cc and bcc data."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        if self.instance:
            payload = self.instance.payload
            self.fields['cc_email'].initial = ', '.join(
                payload.get('cc_email', []))
            self.fields['bcc_email'].initial = ', '.join(
                payload.get('bcc_email', []))

    def clean(self):
        """Verify that the date is correct."""
        form_data = super().clean()

        if not all(
            is_correct_email(email)
            for email in self.cleaned_data['cc_email'].split(',') if email
        ):
            self.add_error(
                'cc_email',
                _('This field must be a comma-separated list of emails.'))

        if not all(
            is_correct_email(email)
            for email in self.cleaned_data['bcc_email'].split(',') if email
        ):
            self.add_error(
                'bcc_email',
                _('This field must be a comma-separated list of emails.'))

        return form_data


class ScheduleItemsForm(ScheduleBasicForm):
    """Form to handle item_column and confirm_items fields."""
    item_column = forms.ModelChoiceField(queryset=Column.objects.none())

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude email addresses before scheduling?'),
    )

    def __init__(self, form_data, *args, **kwargs):
        """Set item_column values."""
        columns = kwargs.pop('columns')
        confirm_items = kwargs.pop('confirm_items')

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].queryset = columns
        self.fields['confirm_items'].initial = confirm_items

    def clean(self):
        form_data = super().clean()

        item_column = self.cleaned_data['item_column']

        # Check if the values in the email column are correct emails
        try:
            column_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[item_column.name])
            if not all(is_correct_email(row['email']) for row in column_data):
                # column has incorrect email addresses
                self.add_error(
                    'item_column',
                    _('The column with email addresses has incorrect values.'))
        except TypeError:
            self.add_error(
                'item_column',
                _('The column with email addresses has incorrect values.'))

        return form_data

    class Meta(ScheduleBasicForm.Meta):
        """Define model, fields and widgets."""

        fields = ('name', 'description_text', 'item_column', 'execute')


class ScheduleTokenForm(forms.Form):
    # Token to use when sending the JSON request
    token = forms.CharField(
        initial='',
        label=_('Authentication Token'),
        strip=True,
        required=True,
        help_text=_('Authentication token provided by the external platform.'),
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'cols': 120,
                'placeholder': _(
                    'Authentication token to be sent with the JSON object.'),
            }),
    )

    instance = None

    def __init__(self, form_data, *args, **kwargs):
        """Set label and required for the item_column field."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['token'].initial = payload.get('token')


class EmailScheduleForm(
    ScheduleMailSubjectForm,
    ScheduleMailCCForm,
    ScheduleItemsForm,
):
    """Form to create/edit objects of the ScheduleAction of type email.

    One of the fields is a reference to a key column, which is a subset of
    the columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Send you a confirmation email'))

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Track if emails are read?'))

    def __init__(self, form_data, *args, **kwargs):
        """Set additional field items."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].label = _(
            'Column in the table containing the email')

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['send_confirmation'].initial = payload.get(
                'send_confirmation', False)
            self.fields['track_read'].initial = payload.get(
                'track_read',
                False,
            )
            self.fields['confirm_items'].initial = bool(
                self.instance.exclude_values)

        self.order_fields([
            'name',
            'description_text',
            'execute',
            'item_column',
            'subject',
            'cc_email',
            'bcc_email',
            'confirm_items',
            'send_confirmation',
            'track_read'])


class SendListScheduleForm(
    ScheduleMailSubjectForm, ScheduleMailCCForm, ScheduleBasicForm
):
    """Form to create/edit objects of the ScheduleAction of type send list."""

    email_to = forms.CharField(label=_('Recipient'), required=True)

    def __init__(self, form_data, *args, **kwargs):
        """Set additional field items."""
        self.action = kwargs.pop('action')

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['email_to'].initial = payload.get('email_to')

        self.order_fields([
            'name',
            'description_text',
            'execute',
            'email_to',
            'subject',
            'cc_email',
            'bcc_email'])

    def clean(self):
        """Process errors and add them to the form."""
        form_data = super().clean()

        if not is_correct_email(form_data['email_to']):
            self.add_error(
                'email_to',
                _('This field must be a valid email address.'))

        return form_data


class JSONScheduleForm(ScheduleTokenForm, ScheduleItemsForm):
    """Form to edit ScheduleAction of types JSON and JSON List."""

    class Meta(ScheduleItemsForm.Meta):
        """Redefine the order."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'execute',
            'token')


class JSONListScheduleForm(ScheduleTokenForm, ScheduleBasicForm):
    """Form to edit ScheduleAction of types JSON List."""

    class Meta(ScheduleBasicForm.Meta):
        """Redefine the order."""

        fields = (
            'name',
            'description_text',
            'execute',
            'token')


class CanvasEmailScheduleForm(ScheduleMailSubjectForm, ScheduleItemsForm):
    """Form to create/edit ScheduleAction of type canvas email."""

    def __init__(self, form_data, *args, **kwargs):
        """Assign item_column field."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].label = _(
            'Column in the table containing the Canvas ID')

    class Meta(ScheduleItemsForm.Meta):
        """Field order."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'subject',
            'execute')
