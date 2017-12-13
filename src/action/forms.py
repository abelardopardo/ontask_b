# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime
import pytz

from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.conf import settings
from django_summernote.widgets import SummernoteInplaceWidget

from .models import Action, Condition
from ontask.forms import column_to_field, dateTimeOptions

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___select_'


class ActionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(str('workflow_user'), None)
        self.workflow = kwargs.pop(str('action_workflow'), None)
        super(ActionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Action
        fields = ('name', 'description_text',)


class EditActionOutForm(forms.ModelForm):
    """
    Main class to edit an action out. The main element is the text editor (
    currently using summernote).
    """
    content = forms.CharField(
        widget=SummernoteInplaceWidget(),
        label='')

    class Meta:
        model = Action
        fields = ('content',)


# Form to select a subset of the columns
class EditActionInForm(forms.ModelForm):
    """
    Main class to edit an action in . The main element is the text editor (
    currently using summernote).
    """

    def __init__(self, *args, **kwargs):

        self.columns = kwargs.pop('columns', [])
        self.selected = kwargs.pop('selected', [])

        super(EditActionInForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['filter'].required = False

        # Filter should be hidden.
        self.fields['filter'].widget = forms.HiddenInput()

        # Create as many fields as the given columns
        for idx in range(len(self.columns)):

            self.fields[field_prefix + '%s' % idx] = forms.BooleanField(
                initial=self.selected[idx],
                label='',
                required=False,
            )

    def clean(self):
        cleaned_data = super(EditActionInForm, self).clean()

        selected_list = [
            cleaned_data.get(field_prefix + '%s' % i, False)
            for i in range(len(self.columns))
        ]

        # Check if at least a unique column has been selected
        both_lists = zip(selected_list, self.columns)
        if not any([a and b.is_key for a, b in both_lists]):
            self.add_error(None, 'No key column specified',)

    class Meta:
        model = Action
        fields = ('filter',)


# Form to enter values in a row
class EnterActionIn(forms.Form):

    def __init__(self, *args, **kargs):

        # Store the instance
        self.columns = kargs.pop('columns', None)
        self.values = kargs.pop('values', None)

        super(EnterActionIn, self).__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.values:
            self.values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):
            self.fields[field_prefix + '%s' % idx] = \
                column_to_field(column,
                                self.values[idx],
                                label=column.description_text)

            if column.is_key:
                self.fields[field_prefix + '%s' % idx].widget.attrs[
                    'readonly'
                ] = 'readonly'
                self.fields[field_prefix + '%s' % idx].disabled = True


class FilterForm(forms.ModelForm):
    """
    Form to read information about a filter. The required property of the
    formula field is set to False because it is enforced in the server.
    """
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

    class Meta:
        model = Condition
        fields = ('name', 'description_text', 'formula')


class ConditionForm(FilterForm):
    """
    Form to read information about a condition. The same as the filter but we
    need to enforce that the name is a valid variable name
    """

    def __init__(self, *args, **kwargs):

        super(ConditionForm, self).__init__(*args, **kwargs)

        # Remember the condition name to perform content substitution
        self.old_name = None,
        if hasattr(self, 'instance'):
            self.old_name = self.instance.name

    def clean(self):
        data = super(ConditionForm, self).clean()

        if ' ' in data['name'] or '-' in data['name']:
            self.add_error(
                'name',
                'Condition names can only have letters, numbers and _'
            )
            return data

        return data


class EnableURLForm(forms.ModelForm):

    def clean(self):
        data = super(EnableURLForm, self).clean()

        # Check the datetimes. One needs to be after the other
        a_from = self.cleaned_data['active_from']
        a_to = self.cleaned_data['active_to']
        if a_from and a_to and a_from >= a_to:
            self.add_error(
                'active_from',
                'Incorrect date/time window'
            )
            self.add_error(
                'active_to',
                'Incorrect date/time window'
            )

        return data

    class Meta:
        model = Action
        fields = ('serve_enabled', 'active_from', 'active_to')

        widgets = {
            'active_from': DateTimeWidget(options=dateTimeOptions,
                                          usel10n=True,
                                          bootstrap_version=3),
            'active_to': DateTimeWidget(options=dateTimeOptions,
                                        usel10n=True,
                                        bootstrap_version=3)
        }


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
        help_text="Number of times the email was opened."
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