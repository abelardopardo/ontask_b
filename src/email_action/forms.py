# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime
import pytz
from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.conf import settings


class EmailActionBasicForm(forms.Form):
    subject = forms.CharField(max_length=1024,
                              strip=True,
                              required=True,
                              label='Email subject')

    email_column = forms.ChoiceField(
        label='Column to use for target email address',
        required=True
    )

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label='Send you a summary message?')

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label="Track email reading?"
    )

    add_column = forms.BooleanField(
        initial=False,
        required=False,
        label="Add a column reflecting the email tracking?",
        help_text="Times the email was opened."
    )

    def __init__(self, *args, **kargs):
        self.column_names = kargs.pop('column_names')

        super(EmailActionBasicForm, self).__init__(*args, **kargs)

        # Try to guess if there is an "email" column
        initial_choice = next((x for x in self.column_names
                               if 'email' == x.lower()), None)

        if initial_choice is None:
            initial_choice = ('', '---')
        else:
            initial_choice = (initial_choice, initial_choice)

        self.fields['email_column'].initial = initial_choice,
        self.fields['email_column'].choices = \
            [(x, x) for x in self.column_names]

    def clean(self):
        data = super(EmailActionBasicForm, self).clean()

        if data['add_column'] and not data['track_read']:
            self.add_error(
                'track_read',
                'To add a column, you need to track email reading'
            )

    class Meta:
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class EmailActionForm(EmailActionBasicForm):
    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label="Download a snapshot of the current state of the workflow?",
        help_text="A zip file useful to review the emails sent."
    )


class EmailScheduleSendForm(EmailActionBasicForm):
    when = forms.DateTimeField(
        label='Time to send the emails',
        required=True,
        widget=DateTimeWidget(
            options={'weekStart': 1, 'minuteStep': 15},
            usel10n=True,
            bootstrap_version=3),
    )

    def clean(self):
        data = super(EmailScheduleSendForm, self).clean()

        # Check the datetime is in the future
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        when_data = self.cleaned_data.get('when', None)
        if when_data and when_data <= now:
            self.add_error(
                'when',
                'Date/time must be in the future'
            )

        return data