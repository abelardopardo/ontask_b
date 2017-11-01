# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django import forms


class EmailActionForm(forms.Form):
    subject = forms.CharField(max_length=1024,
                              strip=True,
                              required=True,
                              label='Email subject')

    email_column = forms.ChoiceField(
        label='Column to use for target email address (mandatory)',
        required=True
    )

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label='Send you a summary message?')

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label="Download a snapshot of the current state of the workflow?",
        help_text="A zip file useful to review the emails sent."
    )

    def __init__(self, *args, **kargs):

        self.column_names = kargs.pop('column_names')

        super(EmailActionForm, self).__init__(*args, **kargs)

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

    class Meta:
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}
