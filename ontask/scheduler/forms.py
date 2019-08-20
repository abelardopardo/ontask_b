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
from ontask.models import ScheduledAction
from ontask.workflow.models import Column


class ScheduleForm(forms.ModelForm):
    """Form to create/edit objects of the ScheduleAction.

    To be used for the various types of actions.

    There is an additional field to allow for an extra step to review and
    filter elements (item_column).
    """

    # This field is needed because it has to consider only a subset of the
    # columns, those that are "key".

    item_column = forms.ModelChoiceField(queryset=Column.objects.none())

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude email addresses before scheduling?'),
    )

    def __init__(self, form_data, *args, **kwargs):
        """Set item_column values."""
        self.action = kwargs.pop('action')
        columns = kwargs.pop('columns')
        confirm_items = kwargs.pop('confirm_items')

        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].queryset = columns
        self.fields['confirm_items'].initial = confirm_items

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

        fields = ('name', 'description_text', 'item_column', 'execute')

        widgets = {
            'execute': DateTimePickerInput(options=date_time_widget_options),
        }


class EmailScheduleForm(ScheduleForm):
    """Form to create/edit objects of the ScheduleAction of type email.

    One of the fields is a reference to a key column, which is a subset of
    the columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

    subject = forms.CharField(
        initial='',
        label=_('Email subject'),
        strip=True,
        required=True)

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
            self.fields['subject'].initial = payload.get('subject')
            self.fields['cc_email'].initial = ', '.join(
                payload.get('cc_email', []))
            self.fields['bcc_email'].initial = ', '.join(
                payload.get('bcc_email', []))
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

    def clean(self):
        """Process errors and add them to the form."""
        form_data = super().clean()

        errors = scheduled_email_action_data_is_correct(
            self.action,
            self.cleaned_data,
        )

        # Pass the errors to the form
        for field, txt in errors:
            self.add_error(field, txt)

        return form_data


class JSONScheduleForm(ScheduleForm):
    """Form to create/edit objects of the ScheduleAction of type email.

    One of the fields is a reference to a key column, which is a subset of
    the columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

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

    def __init__(self, form_data, *args, **kwargs):
        """Set label and required for the item_column field."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].label = _(
            'Column to pick elements to ignore (empty to skip)')
        self.fields['item_column'].required = False
        # No longer needed, item column does the same
        self.fields.pop('confirm_items')

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['token'].initial = payload.get('token')

    def clean(self):
        """Clean the form data."""
        form_data = super().clean()

        errors = scheduled_json_action_data_is_correct(
            self.action,
            self.cleaned_data,
        )

        # Pass the errors to the form
        for field, txt in errors:
            self.add_error(field, txt)

        return form_data

    class Meta(ScheduleForm.Meta):
        """Redefine the order."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'execute',
            'token')


class CanvasEmailScheduleForm(JSONScheduleForm):
    """Form to create/edit objects of the ScheduleAction of type canvas email.

    One of the fields is the canvas ID key column, which is a subset of the
    columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter canvas IDs.
    """

    subject = forms.CharField(
        initial='',
        label=_('Email subject'),
        strip=True,
        required=True)

    def __init__(self, form_data, *args, **kwargs):
        """Assign item_column field."""
        # Call the parent constructor
        super().__init__(form_data, *args, **kwargs)

        self.fields['item_column'].label = _(
            'Column in the table containing the Canvas ID')

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['subject'].initial = payload.get('subject')

    class Meta(JSONScheduleForm.Meta):
        """Field order."""

        fields = (
            'name',
            'description_text',
            'item_column',
            'confirm_items',
            'subject',
            'execute',
            'token')


def scheduled_action_data_is_correct(cleaned_data):
    """Verify the correctness of the object.

    Verify the integrity of a ScheduledAction object with a Personalised_text
    type. The function returns a list of pairs (field name, message) with the
    errors, or [] if no error has been found.

    :param cleaned_data: Data to be verified.

    :return: List of pairs (field name, error) or [] if correct
    """
    pair_list = []

    # The executed time must be in the future
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    when_data = cleaned_data.get('execute')
    if when_data and when_data <= now:
        pair_list.append(
            ('execute', _('Date/time must be in the future')))

    return pair_list


def scheduled_email_action_data_is_correct(action, cleaned_data):
    """Verify email action data.

    Verify the integrity of a ScheduledAction object with a Personalised_text
    type. The function returns a list of pairs (field name, message) with the
    errors, or [] if no error has been found.

    :param action: Action object to use for scheduling

    :param cleaned_data:

    :return: List of pairs (field name, error) or [] if correct
    """
    pair_list = []
    item_column = cleaned_data['item_column']

    # Verify the correct time
    pair_list.extend(scheduled_action_data_is_correct(cleaned_data))

    # Check if the values in the email column are correct emails
    try:
        column_data = get_rows(
            action.workflow.get_data_frame_table_name(),
            column_names=[item_column.name])
        if not all(is_correct_email(row['email']) for row in column_data):
            # column has incorrect email addresses
            pair_list.append(
                ('item_column',
                 _('The column with email addresses has incorrect values.')),
            )
    except TypeError:
        pair_list.append(
            ('item_column',
             _('The column with email addresses has incorrect values.')),
        )

    if not all(
        is_correct_email(email)
        for email in cleaned_data['cc_email'].split(',') if email
    ):
        pair_list.append(
            ('cc_email',
             _('This field must be a comma-separated list of emails.')),
        )

    if not all(
        is_correct_email(email)
        for email in cleaned_data['bcc_email'].split(',') if email
    ):
        pair_list.append(
            ('bcc_email',
             _('This field must be a comma-separated list of emails.')),
        )

    return pair_list


def scheduled_json_action_data_is_correct(action, cleaned_data):
    """Verify json data.

    Function to impose extra correct conditions in the JSON schedule data.

    :param action: Action used for the verification

    :param cleaned_data: Data just collected by the form

    :return: List of (string, form element) to attach errors.
    """
    return scheduled_action_data_is_correct(cleaned_data)
