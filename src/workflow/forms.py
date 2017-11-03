# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json
import pandas as pd

from django import forms

from dataops import pandas_db, ops
from ontask import is_legal_var_name
from ontask import ontask_prefs
from ontask.forms import RestrictedFileField
from .models import Workflow, Column


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

            self.instance.set_categories(valid_values)

        return data

    class Meta:
        model = Column
        fields = ('name', 'data_type', 'raw_categories')


class ColumnAddForm(ColumnBasicForm):

    # initial value
    initial_value = forms.CharField(
        max_length=512,
        strip=True,
        required=False,
        label='Value to assign to all cells in the column'
    )

    def clean(self):
        data = super(ColumnBasicForm, self).clean()

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
        fields = ('name', 'data_type')


class ColumnRenameForm(ColumnBasicForm):

    def __init__(self, *args, **kwargs):

        super(ColumnRenameForm, self).__init__(*args, **kwargs)

        self.fields['data_type'].widget.attrs['readonly'] = 'readonly'

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

        # Categories must be valid types
        if 'raw_categories' in self.changed_data:
            # Check if the existing values in the column comply with the
            # proposed categories
            valid_values = self.instance.get_categories()
            if not all([x in valid_values
                        for x in self.data_frame[data['name']]
                        if x and not pd.isnull(x)]):
                self.add_error(
                    'raw_categories',
                    'Current column values are different from allowed ones.'
                )
                return data

    class Meta:
        model = Column
        fields = ('name', 'data_type', 'is_key')


class WorkflowImportForm(forms.Form):
    # Worflow name
    name = forms.CharField(
        max_length=512,
        strip=True,
        required=True,
        label='Workflow name',
        help_text='If false only the action text will be included')

    file = RestrictedFileField(
        max_upload_size=str(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label="",
        help_text='File containing a previously exported workflow')

    # Include data and conditions?
    include_data_and_cond = forms.BooleanField(
        label='Include data and conditions (if available)?',
        initial=True,
        required=False)


class WorkflowExportRequestForm(forms.Form):
    # Include data and conditions?
    include_data_and_cond = forms.BooleanField(
        label='Include data and conditions in export?',
        initial=True,
        required=False)
