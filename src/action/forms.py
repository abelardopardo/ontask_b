# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.forms.widgets import SelectMultiple
from django_summernote.widgets import SummernoteInplaceWidget

from ontask import is_legal_name
from ontask.forms import column_to_field, dateTimeOptions
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


# Form to select a subset of the columns
class EditActionInForm(forms.ModelForm):
    """
    Main class to edit an action in. Two elements appear in the form. The
    filter expression to select a subset of rows from the table, and a widget
    to select multiple columns.
    """

    # Columns to to select
    columns = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, data, *args, **kwargs):
        # Get the workflow to access the columns
        workflow = kwargs.pop('workflow', None)

        super(EditActionInForm, self).__init__(data, *args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['filter'].required = False

        # Filter should be hidden.
        self.fields['filter'].widget = forms.HiddenInput()

        # The queryset for the columns must be extracted from the workflow
        self.fields['columns'].queryset = workflow.columns.all()

    def clean(self):
        data = super(EditActionInForm, self).clean()

        # Check if there is at least one key column
        if not any([a.is_key for a in data['columns']]):
            self.add_error(
                None,
               'There must be at least one unique column in the view')

        # Check if there is at least one non-key column
        if not any([not a.is_key for a in data['columns']]):
            self.add_error(
                None,
                'There must be at least one non-unique column in the view')

        return data

    class Meta:
        model = Action
        fields = ('name', 'description_text', 'columns', 'filter')


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
        label="Add column to track email reading?",
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
