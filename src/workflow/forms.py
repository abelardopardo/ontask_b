# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

import pandas as pd
from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from dataops import pandas_db, ops
from ontask import is_legal_var_name, ontask_prefs
from ontask.forms import RestrictedFileField, dateTimeOptions
from .models import Workflow, Column


# Options for the datetime picker used in column forms


class WorkflowForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('workflow_user', None)
        super(WorkflowForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Workflow
        fields = ('name', 'description_text',)


class AttributeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.form_fields = kwargs.pop('form_fields')
        super(AttributeForm, self).__init__(*args, **kwargs)

        # Create the set of fields
        for key, val_field, val in self.form_fields:
            # Field for the key
            self.fields[key] = forms.CharField(
                max_length=1024,
                initial=key,
                strip=True,
                label='')

            # Field for the value
            self.fields[val_field] = forms.CharField(
                max_length=1024,
                initial=val,
                label='')

    def clean(self):
        data = super(AttributeForm, self).clean()

        new_keys = [data[x] for x, _, _ in self.form_fields]

        # Check that there were not duplicate keys given
        if len(set(new_keys)) != len(new_keys):
            raise forms.ValidationError(
                'Repeated names are not allowed'
            )

        return data


class AttributeItemForm(forms.Form):
    # Key field
    key = forms.CharField(max_length=1024,
                          strip=True,
                          required=True,
                          label='Name')

    # Field for the value
    value = forms.CharField(max_length=1024,
                            label='Value')

    def __init__(self, *args, **kwargs):
        self.keys = kwargs.pop('keys')
        super(AttributeItemForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(AttributeItemForm, self).clean()

        if ' ' in data['key'] or '-' in data['key']:
            self.add_error(
                'key',
                'Attribute names can only have letters, numbers and _'
            )
            return data

        if data['key'] in self.keys:
            self.add_error(
                'key',
                'Name has to be different from the existing ones.')
            return data

        return data


class ColumnBasicForm(forms.ModelForm):
    # Raw text for the categories
    raw_categories = forms.CharField(
        strip=True,
        required=False,
        label='Comma separated list of allowed values')

    def __init__(self, *args, **kwargs):

        self.workflow = kwargs.pop('workflow', None)
        self.data_frame = None

        super(ColumnBasicForm, self).__init__(*args, **kwargs)

        self.fields['raw_categories'].initial = \
            ', '.join([str(x) for x in self.instance.get_categories()])

    def clean(self):
        data = super(ColumnBasicForm, self).clean()

        # Load the data frame from the DB for various checks and leave it in
        # the form for future use
        self.data_frame = pandas_db.load_from_db(self.workflow.id)

        # Column name must be a legal variable name
        if 'name' in self.changed_data:
            if not is_legal_var_name(data['name']):
                self.add_error(
                    'name',
                    'Column name must start with a letter or _ '
                    'followed by letters, numbers or _'
                )
                return data

            # Check that the name is not present already
            if next((c for c in self.workflow.columns.all()
                     if c.id != self.instance.id and
                        c.name == data['name']), None):
                # New column name collides with existing one
                self.add_error(
                    'name',
                    'There is a column already with this name'
                )
                return data

        # Categories must be valid types
        if 'raw_categories' in self.changed_data:
            if data['raw_categories']:
                # Condition 1: Values must be valid for the type of the column
                category_values = [x.strip()
                                   for x in data['raw_categories'].split(',')]
                try:
                    valid_values = Column.validate_column_values(
                        data['data_type'],
                        category_values)
                except ValueError:
                    self.add_error(
                        'raw_categories',
                        'Incorrect list of values'
                    )
                    return data

                # Condition 2: The values in the dataframe column must be in
                # these categories (only if the column is being edited, though
                if self.instance.name and \
                        not all([x in valid_values
                                 for x in self.data_frame[self.instance.name]
                                 if x and not pd.isnull(x)]):
                    self.add_error(
                        'raw_categories',
                        'The values in the column are not compatible with ' +
                        'these ones.'
                    )
                    return data
            else:
                valid_values = []

            self.instance.set_categories(valid_values)

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
        model = Column
        fields = ['name', 'description_text', 'data_type', 'raw_categories',
                  'active_from', 'active_to']

        widgets = {
            'active_from': DateTimeWidget(options=dateTimeOptions,
                                          usel10n=True,
                                          bootstrap_version=3),
            'active_to': DateTimeWidget(options=dateTimeOptions,
                                        usel10n=True,
                                        bootstrap_version=3)
        }


class ColumnAddForm(ColumnBasicForm):
    # initial value
    initial_value = forms.CharField(
        max_length=512,
        strip=True,
        required=False,
        label='Value to assign to all cells in the column'
    )

    def clean(self):
        data = super(ColumnAddForm, self).clean()

        # Try to convert the initial value ot the right type
        initial_value = data['initial_value']

        self.initial_valid_value = None
        if initial_value:
            try:
                self.initial_valid_value = Column.validate_column_value(
                    data['data_type'],
                    initial_value
                )
            except ValueError:
                self.add_error(
                    'initial_value',
                    'Incorrect initial value'
                )
                return data

        return data

    class Meta:
        model = Column
        fields = ['name', 'description_text', 'data_type', 'active_from',
                  'active_to']

        widgets = {
            'active_from': DateTimeWidget(options=dateTimeOptions,
                                          usel10n=True,
                                          bootstrap_version=3),
            'active_to': DateTimeWidget(options=dateTimeOptions,
                                        usel10n=True,
                                        bootstrap_version=3)
        }


class ColumnRenameForm(ColumnBasicForm):

    def __init__(self, *args, **kwargs):

        super(ColumnRenameForm, self).__init__(*args, **kwargs)

        self.fields['data_type'].disabled = True

    def clean(self):

        data = super(ColumnRenameForm, self).clean()

        # Check if there has been a change in the 'is_key' status
        if 'is_key' in self.changed_data:
            # Case 1: True -> False If it is the only one, cannot be
            # allowed
            column_unique = self.instance.workflow.get_column_unique()
            if self.instance.is_key and \
                    len([x for x in column_unique if x]) == 1:
                self.add_error(
                    'is_key',
                    'There must be at least one column with unique values'
                )
                return data

            # Case 2: False -> True Unique values must be verified
            if not self.instance.is_key and \
                    not ops.is_unique_column(self.data_frame[
                                                 self.instance.name]):
                self.add_error(
                    'is_key',
                    'The column does not have unique values for each row.'
                )
                return data

        return data

    class Meta:
        model = Column
        fields = ['name', 'description_text', 'data_type', 'is_key',
                  'active_from', 'active_to']

        widgets = {
            'active_from': DateTimeWidget(options=dateTimeOptions,
                                          usel10n=True,
                                          bootstrap_version=3),
            'active_to': DateTimeWidget(options=dateTimeOptions,
                                        usel10n=True,
                                        bootstrap_version=3)
        }


class WorkflowImportForm(forms.Form):
    # Worflow name
    name = forms.CharField(
        max_length=512,
        strip=True,
        required=True,
        label='Name')

    file = RestrictedFileField(
        max_upload_size=str(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label="File",
        help_text='File containing a previously exported workflow')


class WorkflowExportRequestForm(forms.Form):

    def __init__(self, *args, **kargs):
        """
        Kargs contain: actions: list of action objects, put_labels: boolean
        stating if the labels should be included in the form
        :param args:
        :param kargs:
        """
        # List of columns to process and a field prefix
        self.actions = kargs.pop('actions', [])
        self.field_prefix = kargs.pop('field_prefix', 'select_')

        # Should the labels be included?
        self.put_labels = kargs.pop('put_labels', False)

        super(WorkflowExportRequestForm, self).__init__(*args, **kargs)

        # Create as many fields as the given columns
        for i, a in enumerate(self.actions):
            # Include the labels if requested
            if self.put_labels:
                label = a.name
            else:
                label = ''

            self.fields[self.field_prefix + '%s' % i] = forms.BooleanField(
                label=label,
                label_suffix='',
                required=False,
            )


class SharedForm(forms.Form):
    """
    Form to ask for a user email to add to those sharing the workflow. The
    form uses two parameters:
    :param user: The user making the request (to detect self-sharing)
    :param workflow: The workflow to share (to detect users already in the
     list)
    """
    user_email = forms.CharField(max_length=1024,
                                 strip=True,
                                 label='User email')

    def __init__(self, *args, **kwargs):

        self.request_user = kwargs.pop('user', None)
        self.workflow = kwargs.pop('workflow')
        self.user_obj = None

        super(SharedForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(SharedForm, self).clean()

        try:
            self.user_obj = get_user_model().objects.get(
                email__iexact=data['user_email']
            )
        except ObjectDoesNotExist:
            self.add_error('user_email', 'User not found')

        if self.user_obj == self.request_user:
            self.add_error(
                'user_email',
                "You don't need to add yourself to the share list"
            )

        if self.user_obj in self.workflow.shared.all():
            self.add_error(
                'user_email',
                "User already in the list"
            )

        return data
