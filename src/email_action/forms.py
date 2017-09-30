# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from action.models import Action


class EmailActionForm(forms.Form):

    subject = forms.CharField(max_length=1024,
                              strip=True,
                              required=True,
                              label='Email subject')

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label='Send you a summary message?')

    # track_read = forms.BooleanField(
    #     initial=False,
    #     required=False,
    #     label="Track email reading?"
    # )
    #
    # track_column = forms.BooleanField(
    #     initial=False,
    #     required=False,
    #     label="Add tracking as new column matrix?",
    #     help_text="A boolean column stating if the email was opened."
    # )
    #
    # sent_column = forms.BooleanField(
    #     initial=False,
    #     required=False,
    #     label='Add a column with True/False if email was sent'
    # )

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

        self.fields['email_column'] = forms.ChoiceField(
            initial=initial_choice,
            choices=[(x, x) for x in self.column_names],
            label='Column to use for target email address',
            required=True
        )

    class Meta:
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}
