# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime

import pytz
from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.conf import settings

from core import settings as core_settings
from workflow.models import Column
from .models import ScheduledEmailAction


class EmailForm(forms.ModelForm):
    """
    Form to create/edit objects of the ScheduleEmailAction. One of the fields
    is a reference to a key column, which is a subset of the columns attached
    to the action. The subset is passed as the name arguments "columns" (list
    of key columns).
    """
    # This field is needed because it has to consider only a subset of the
    # columns, those that are "key".
    email_column = forms.ModelChoiceField(queryset=Column.objects.none())

    def __init__(self, data, *args, **kwargs):

        columns = kwargs.pop('columns')

        # Call the parent constructor
        super(EmailForm, self).__init__(data, *args, **kwargs)

        self.fields['email_column'].queryset = columns

    def clean(self):

        data = super(EmailForm, self).clean()

        # The executed time must be in the future
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        when_data = self.cleaned_data.get('execute', None)
        if when_data and when_data <= now:
            self.add_error('execute', 'Date/time must be in the future')

        return data

    class Meta:
        model = ScheduledEmailAction
        fields = ('subject', 'email_column', 'send_confirmation', 'track_read',
                  'execute')

        widgets = {
            'execute': DateTimeWidget(
                options={'weekStart': 1,
                         'minuteStep': str(getattr(core_settings,
                                                   'MINUTE_STEP'))},
                usel10n=True,
                bootstrap_version=3),
        }
