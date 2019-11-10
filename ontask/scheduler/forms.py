# -*- coding: utf-8 -*-

"""Forms for scheduling actions."""

import datetime

import pytz
from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _

from ontask import is_correct_email
from ontask.action import forms as action_forms
from ontask.core import forms as ontask_forms
from ontask.dataops.sql.row_queries import get_rows
from ontask.models import Column, ScheduledOperation


class ScheduleBasicForm(ontask_forms.FormWithPayloadAbstract, forms.ModelForm):
    """Form to create/edit objects of the ScheduleAction.

    To be used for the various types of actions.
    """
    action = None

    def __init__(self, form_data, *args, **kwargs):
        """Set item_column values."""
        super().__init__(form_data, *args, **kwargs)

        self.set_fields_from_dict(['name', 'description_text'])
        self.fields['execute'].initial = parse_datetime(
                self.get_payload_field('execute', ''))
        self.fields['execute_until'].initial = parse_datetime(
                self.get_payload_field('execute_until', ''))

    def clean(self):
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

    class Meta(object):
        """Define model, fields and widgets."""

        model = ScheduledOperation
        fields = ('name', 'description_text', 'execute', 'execute_until')
        widgets = {
            'execute': DateTimePickerInput(
                options=ontask_forms.date_time_widget_options),
            'execute_until':
                DateTimePickerInput(
                    options=ontask_forms.date_time_widget_options)}


class ScheduleMailSubjectForm(ontask_forms.FormWithPayload):
    subject = forms.CharField(
        initial='',
        label=_('Email subject'),
        strip=True,
        required=True)

    def __init__(self, form_data, *args, **kwargs):
        """Set subject value."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.set_field_from_dict('subject')

    def clean(self):
        form_data = super().clean()
        self.store_field_in_dict('subject')
        return form_data

class ScheduleMailCCForm(ontask_forms.FormWithPayload):
    cc_email = forms.CharField(
        initial='',
        label=_('CC Emails (separated by spaces)'),
        strip=True,
        required=False)

    bcc_email = forms.CharField(
        initial='',
        label=_('List of BCC Emails (separated by spaces)'),
        strip=True,
        required=False)

    instance = None

    def __init__(self, form_data, *args, **kwargs):
        """Set cc and bcc data."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.set_fields_from_dict(['cc_email', 'bcc_email'])

    def clean(self):
        """Verify that the date is correct."""
        form_data = super().clean()

        self.store_fields_in_dict([
            (
                'cc_email',
                (' ').join([
                    email.strip()
                    for email in form_data['cc_email'].split() if email
                ])
            ),
            (
                'bcc_email',
                (' ').join([
                    email.strip()
                    for email in form_data['bcc_email'].split() if email
                ])
            )])

        if not all(
            is_correct_email(email) for email in form_data['cc_email'].split()
        ):
            self.add_error(
                'cc_email',
                _('This field must be a comma-separated list of emails.'))

        if not all(
            is_correct_email(email) for email in form_data['bcc_email'].split()
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

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.set_field_from_dict('confirm_items')
        if self.instance and self.instance.exclude_values:
            self.fields['confirm_items'].initial = True

        # Special case: get the column from the name
        self.fields['item_column'].queryset = columns
        column_name = self._FormWithPayload__form_info.get('item_column')
        if column_name:
            column = self.action.workflow.columns.get(name=column_name)
            self.fields['item_column'].initial = column.pk

    def clean(self):
        form_data = super().clean()

        self.store_fields_in_dict([
            ('item_column', form_data['item_column'].name),
            ('confirm_items', None)])

        item_column = self.cleaned_data['item_column']

        # Check if the values in the email column are correct emails
        try:
            column_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[item_column.name])
            if not all(
                is_correct_email(row[item_column.name]) for row in column_data
            ):
                # column has incorrect email addresses
                self.add_error(
                    'item_column',
                    _('The column with email addresses has incorrect values.'))
        except TypeError:
            self.add_error(
                'item_column',
                _('The column with email addresses has incorrect values.'))

        if self.instance and not form_data['confirm_items']:
            self.instance.exclude_values = []

        return form_data

    class Meta(ScheduleBasicForm.Meta):
        """Define model, fields and widgets."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'execute',
            'execute_until')


class ScheduleTokenForm(ontask_forms.FormWithPayload):
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

        self.set_field_from_dict('token')

    def clean(self):
        """Store the values in the form info."""
        form_data = super().clean()
        self.store_field_in_dict('token', None)
        return form_data


class EmailScheduleForm(
    ontask_forms.FormWithPayload,
    ScheduleBasicForm,
    action_forms.EmailActionForm,
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

        self.set_fields_from_dict(['send_confirmation', 'track_read'])
        self.fields['item_column'].label = _(
            'Column in the table containing the email')

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

    def clean(self):
        """Store the values in the form info."""
        form_data = super().clean()
        self.store_fields_in_dict([
            ('send_confirmation', None),
            ('track_read', None)
        ])
        return form_data


class SendListScheduleForm(
    ontask_forms.FormWithPayload,
    ScheduleBasicForm,
    action_forms.SendListActionForm,
):
    """Form to create/edit objects of the ScheduleAction of type send list."""

    def __init__(self, form_data, *args, **kwargs):
        """Set additional field items."""
        columns = kwargs.pop('columns')

        # Call the parent constructor
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

    def clean(self):
        """Process errors and add them to the form."""
        form_data = super().clean()

        self.store_field_in_dict('email_to')

        if not is_correct_email(form_data['email_to']):
            self.add_error(
                'email_to',
                _('This field must be a valid email address.'))

        return form_data


class JSONScheduleForm(
    ontask_forms.FormWithPayload,
    ScheduleBasicForm,
    action_forms.JSONActionForm,
):
    """Form to edit ScheduleAction of type JSON."""

    class Meta(ScheduleItemsForm.Meta):
        """Redefine the order."""

        fields = (
            'name',
            'description_text',
            'execute',
            'execute_until',
            'item_column',
            'confirm_items',
            'token')


class JSONListScheduleForm(
    ontask_forms.FormWithPayload,
    ScheduleBasicForm,
    action_forms.JSONListActionForm,
):
    """Form to edit ScheduleAction of types JSON List."""

    def __init__(self, form_data, *args, **kwargs):
        """Set additional field items."""
        columns = kwargs.pop('columns')

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.order_fields([
            'name',
            'description_text',
            'execute',
            'execute_until',
            'token'])

    class Meta(ScheduleBasicForm.Meta):
        """Redefine the order."""

        fields = (
            'name',
            'description_text',
            'execute',
            'execute_until',
            'token')


class CanvasEmailScheduleForm(
    ontask_forms.FormWithPayload,
    ScheduleBasicForm,
    action_forms.CanvasEmailActionForm,
):
    """Form to schedule Action of type canvas email."""

    def __init__(self, form_data, *args, **kwargs):
        """Assign item_column field."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.order_fields([
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'subject',
            'execute',
            'execute_until'])

    class Meta(ScheduleItemsForm.Meta):
        """Field order."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'subject',
            'execute',
            'execute_until')
