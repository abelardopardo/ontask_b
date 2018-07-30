# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from datetimewidget.widgets import DateTimeWidget
from django import forms
from django_summernote.widgets import SummernoteInplaceWidget
from django.utils.translation import ugettext_lazy as _

from ontask import ontask_prefs, is_legal_name
from ontask.forms import column_to_field, dateTimeOptions, RestrictedFileField
from .models import Action, Condition

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


class ActionDescriptionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ('description_text',)


class EditActionOutForm(forms.ModelForm):
    """
    Main class to edit an action out. The main element is the text editor (
    currently using summernote).
    """
    content = forms.CharField(
        widget=SummernoteInplaceWidget(),
        label='',
        required=False)

    class Meta:
        model = Action
        fields = ('content',)


# Form to enter values in a row
class EnterActionIn(forms.Form):

    def __init__(self, *args, **kargs):

        # Store the instance
        self.columns = kargs.pop('columns', None)
        self.values = kargs.pop('values', None)
        self.show_key = kargs.pop('show_key', False)

        super(EnterActionIn, self).__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.values:
            self.values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):

            # Skip the key columns if flag is true
            if not self.show_key and column.is_key:
                continue

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

        msg = is_legal_name(data['name'])
        if msg:
            self.add_error('name', msg)
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
                _('Incorrect date/time window')
            )
            self.add_error(
                'active_to',
                _('Incorrect date/time window')
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
                              label=_('Email subject'))

    email_column = forms.ChoiceField(
        label=_('Column to use for target email address'),
        required=True
    )

    cc_email = forms.CharField(
        label='Comma separated list of CC emails',
        required=False
    )
    bcc_email = forms.ChoiceField(
        label='Comma separated list of BCC emails',
        required=False
    )

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Send you a summary message?'))
    )

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Track email reading in an extra column?')
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

    class Meta:
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class EmailActionForm(EmailActionBasicForm):
    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the current state of the workflow?'),
        help_text=_('A zip file useful to review the emails sent.')
    )


class ActionImportForm(forms.Form):
    # Action name
    name = forms.CharField(
        max_length=512,
        strip=True,
        required=True,
        label='Name')

    file = RestrictedFileField(
        max_upload_size=str(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File'),
        help_text=_('File containing a previously exported action'))
