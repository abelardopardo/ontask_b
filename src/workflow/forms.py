# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

import pandas as pd
from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from dataops import pandas_db, ops
from ontask import ontask_prefs, is_legal_name
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


class AttributeItemForm(forms.Form):
    # Key field
    key = forms.CharField(max_length=1024,
                          strip=True,
                          required=True,
                          label=_('Name'))

    # Field for the value
    value = forms.CharField(max_length=1024,
                            label='Value')

    def __init__(self, *args, **kwargs):
        self.keys = kwargs.pop('keys')

        key = kwargs.pop('key', '')
        value = kwargs.pop('value', '')

        super(AttributeItemForm, self).__init__(*args, **kwargs)

        self.fields['key'].initial = key
        self.fields['value'].initial = value

    def clean(self):
        data = super(AttributeItemForm, self).clean()

        # Name is legal
        msg = is_legal_name(data['key'])
        if msg:
            self.add_error('key', msg)
            return data

        if data['key'] in self.keys:
            self.add_error(
                'key',
                _('Name has to be different from all existing ones.'))
            return data

        return data


class ColumnBasicForm(forms.ModelForm):
    # Raw text for the categories
    raw_categories = forms.CharField(
        strip=True,
        required=False,
        label=_('Comma separated list of values allowed in this column'))

    data_type_choices = [
        ('double', 'number'),
        ('integer', 'number'),
        ('string', 'string'),
        ('boolean', 'boolean'),
        ('datetime', 'datetime')
    ]

    def __init__(self, *args, **kwargs):

        self.workflow = kwargs.pop('workflow', None)
        self.data_frame = None

        super(ColumnBasicForm, self).__init__(*args, **kwargs)

        self.fields['raw_categories'].initial = \
            ', '.join([str(x) for x in self.instance.get_categories()])

        self.fields['data_type'].choices = self.data_type_choices

    def clean(self):

        data = super(ColumnBasicForm, self).clean()

        # Load the data frame from the DB for various checks and leave it in
        # the form for future use
        self.data_frame = pandas_db.load_from_db(self.workflow.id)

        # Column name must be a legal variable name
        if 'name' in self.changed_data:
            # Name is legal
            msg = is_legal_name(data['name'])
            if msg:
                self.add_error('name', msg)
                return data

            # Check that the name is not present already
            if next((c for c in self.workflow.columns.all()
                     if c.id != self.instance.id and
                        c.name == data['name']), None):
                # New column name collides with existing one
                self.add_error(
                    'name',
                    _('There is a column already with this name')
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
                        _('Incorrect list of values')
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
                        _('The values in the column are not compatible ' +
                          ' with these ones.')
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
                _('Incorrect date/time window')
            )
            self.add_error(
                'active_to',
                _('Incorrect date/time window')
            )

        return data

    class Meta:
        model = Column
        fields = ['name', 'description_text', 'data_type',
                  'position', 'raw_categories',
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
        label=_('Value to assign to all cells in the column')
    )

    def __init__(self, *args, **kwargs):

        super(ColumnAddForm, self).__init__(*args, **kwargs)

        self.initial_valid_value = None

        self.fields['data_type'].choices = self.data_type_choices[1:]

    def clean(self):

        data = super(ColumnAddForm, self).clean()

        # Try to convert the initial value ot the right type
        initial_value = data['initial_value']
        if initial_value:
            # See if the given value is allowed for the column data type
            try:
                self.initial_valid_value = Column.validate_column_value(
                    data['data_type'],
                    initial_value
                )
            except ValueError:
                self.add_error(
                    'initial_value',
                    _('Incorrect initial value')
                )

            categories = self.instance.get_categories()
            if categories and self.initial_valid_value not in categories:
                self.add_error(
                    'initial_value',
                    _('This value is not in the list of allowed values')
                )

        # Check and force a correct column index
        ncols = Column.objects.filter(workflow__id=self.workflow.id).count()
        if data['position'] < 1 or data['position'] > ncols:
            data['position'] = ncols + 1

        return data

    class Meta(ColumnBasicForm.Meta):
        fields = ['name', 'description_text', 'data_type',
                  'position', 'active_from',
                  'active_to']


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
                    _('There must be at least one column with unique values')
                )
                return data

            # Case 2: False -> True Unique values must be verified
            if not self.instance.is_key and \
                    not ops.is_unique_column(self.data_frame[
                                                 self.instance.name]):
                self.add_error(
                    'is_key',
                    _('The column does not have unique values for each row.')
                )
                return data

        # Check and force a correct column index
        ncols = Column.objects.filter(workflow__id=self.workflow.id).count()
        if data['position'] < 1 or data['position'] > ncols:
            data['position'] = ncols

        return data

    class Meta(ColumnBasicForm.Meta):
        fields = ['name', 'description_text', 'data_type', 'position', 'is_key',
                  'active_from', 'active_to']


class FormulaColumnAddForm(forms.ModelForm):
    # Columns to combine
    columns = forms.MultipleChoiceField([],
                                        required=False,
                                        label=_('Columns to combine*'))

    # Type of operation
    op_type = forms.ChoiceField(
        required=True,
        label='Operation')

    def __init__(self, data, *args, **kwargs):
        # Operands for the new derived column
        self.operands = kwargs.pop('operands')
        # Workflow columns
        self.wf_columns = kwargs.pop('columns')

        super(FormulaColumnAddForm, self).__init__(data, *args, **kwargs)

        # Populate the column choices
        self.fields['columns'].choices = [
            (idx, c.name) for idx, c in enumerate(self.wf_columns)
        ]

        # Populate the operand choices
        self.fields['op_type'].choices = [('', '---')] \
                                         + [(a, b) for a, b, _ in self.operands]

    def clean(self):
        data = super(FormulaColumnAddForm, self).clean()

        # If there are no columns given, return
        column_idx_str = data.get('columns')
        if not column_idx_str:
            self.add_error(
                None,
                _('You need to select the columns to combine')
            )
            return data

        # Get the list of columns selected in the form
        self.selected_columns = [self.wf_columns[int(idx)]
                                 for idx in column_idx_str]

        # Get the set of data types in the selected columns
        result_type = set([x.data_type for x in self.selected_columns])

        # Get the operand
        operand = next((x for x in self.operands if x[0] == data['op_type']),
                       None)

        # The data type of the operand must be contained in the set of allowed
        if not result_type.issubset(set(operand[2])):
            self.add_error(
                None,
                _('Incorrect data type for the selected operand')
            )
            return data

        # Check and force a correct column index
        ncols = self.wf_columns.count()
        if data['position'] < 1 or data['position'] > ncols:
            data['position'] = ncols + 1

        return data

    class Meta(ColumnBasicForm.Meta):
        fields = ['name',
                  'description_text',
                  'position',
                  'op_type',
                  'columns',
                  'active_from',
                  'active_to']


class RandomColumnAddForm(forms.ModelForm):
    # Columns to combine
    values = forms.CharField(
        strip=True,
        required=True,
        label=_('Number (values from 1 to N) or comma separated list of '
                'values.')
    )

    class Meta(ColumnBasicForm.Meta):
        fields = ['name',
                  'description_text',
                  'position',
                  'active_from',
                  'active_to']


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
        label=_("File"),
        help_text=_('File containing a previously exported workflow'))


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
                                 label=_('User email'))

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
            self.add_error('user_email', _('User not found'))

        if self.user_obj == self.request_user:
            self.add_error(
                'user_email',
                _("You don't need to add yourself to the share list")
            )

        if self.user_obj in self.workflow.shared.all():
            self.add_error(
                'user_email',
                _("User already in the list")
            )

        return data
