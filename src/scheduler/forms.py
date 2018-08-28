# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime

import pytz
from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from validate_email import validate_email

from core import settings as core_settings
from dataops.pandas_db import execute_select_on_table
from workflow.models import Column
from .models import ScheduledAction


class ScheduleForm(forms.ModelForm):
    """
    Form to create/edit objects of the ScheduleAction. To be used for the
    various types of actions.

    There is an additional field to allow for an extra step to review and
    filter elements (item_column).
    """

    # This field is needed because it has to consider only a subset of the
    # columns, those that are "key".
    item_column = forms.ModelChoiceField(queryset=Column.objects.none())

    def __init__(self, data, *args, **kwargs):
        self.action = kwargs.pop('action')
        columns = kwargs.pop('columns')

        # Call the parent constructor
        super(ScheduleForm, self).__init__(data, *args, **kwargs)

        self.fields['item_column'].queryset = columns

    def clean(self):

        data = super(ScheduleForm, self).clean()

        # The executed time must be in the future
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        when_data = self.cleaned_data.get('execute', None)
        if when_data and when_data <= now:
            self.add_error('execute',
                           _('Date/time must be in the future'))

        return data

    class Meta:
        model = ScheduledAction
        fields = ('item_column', 'execute')

        widgets = {
            'execute': DateTimeWidget(
                options={'weekStart': 1,
                         'minuteStep': str(getattr(core_settings,
                                                   'MINUTE_STEP'))},
                usel10n=True,
                bootstrap_version=3),
        }


class EmailScheduleForm(ScheduleForm):
    """
    Form to create/edit objects of the ScheduleAction of type email. One of the
    fields is a reference to a key column, which is a subset of the columns
    attached to the action. The subset is passed as the name arguments
    "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

    subject = forms.CharField(initial='',
                              label=_('Email subject'),
                              strip=True,
                              required=True)

    cc_email = forms.CharField(initial='',
                               label=_('Comma-separated list of CC Emails'),
                               strip=True,
                               required=False)

    bcc_email = forms.CharField(initial='',
                                label=_('Comma-separated list of BCC Emails'),
                                strip=True,
                                required=False)

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Send you a confirmation email')
    )

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Track if emails are read?')
    )

    confirm_emails = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude email addresses before scheduling?')
    )

    def __init__(self, data, *args, **kwargs):
        confirm_emails = kwargs.pop('confirm_emails')

        # Call the parent constructor
        super(EmailScheduleForm, self).__init__(data, *args, **kwargs)

        self.fields['item_column'].label = _('Column in the table containing '
                                             'the email')

        self.fields['confirm_emails'].initial = confirm_emails

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['subject'].initial = payload.get('subject')
            self.fields['cc_email'].initial = \
                ', '.join(payload.get('cc_email', []))
            self.fields['bcc_email'].initial = \
                ', '.join(payload.get('bcc_email', []))
            self.fields['send_confirmation'].initial = \
                payload.get('send_confirmation', False)
            self.fields['track_read'].initial = payload.get('track_read', False)

    def clean(self):

        data = super(EmailScheduleForm, self).clean()

        item_column = self.cleaned_data['item_column']

        # Check if the values in the email column are correct emails
        try:
            column_data = execute_select_on_table(
                self.action.workflow.id,
                [],
                [],
                column_names=[item_column.name])
            if not all([validate_email(x[0]) for x in column_data]):
                # column has incorrect email addresses
                self.add_error(
                    'item_column',
                    _('The column with email addresses has incorrect values.')
                )
        except TypeError:
            self.add_error(
                'item_column',
                _('The column with email addresses has incorrect values.')
            )

        if not all([validate_email(x)
                    for x in self.cleaned_data['cc_email'].split(',') if x]):
            self.add_error(
                'cc_email',
                _('This field must be a comma-separated list of emails.')
            )

        if not all([validate_email(x)
                    for x in self.cleaned_data['bcc_email'].split(',') if x]):
            self.add_error(
                'bcc_email',
                _('This field must be a comma-separated list of emails.')
            )

        return data


class JSONScheduleForm(ScheduleForm):
    """
    Form to create/edit objects of the ScheduleAction of type email. One of the
    fields is a reference to a key column, which is a subset of the columns
    attached to the action. The subset is passed as the name arguments
    "columns" (list of key columns).

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
                'placeholder': _('Authentication token to be sent with the '
                                 'JSON object.')
            }
        )
    )

    def __init__(self, data, *args, **kwargs):

        # Call the parent constructor
        super(JSONScheduleForm, self).__init__(data, *args, **kwargs)

        self.fields['item_column'].label = _('Column to select elements ('
                                             'empty to skip)')
        self.fields['item_column'].required = False

        # If there is an instance, push the values in the payload to the form
        if self.instance:
            payload = self.instance.payload
            self.fields['token'].initial = payload.get('token')
