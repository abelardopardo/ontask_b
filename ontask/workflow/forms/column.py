# -*- coding: utf-8 -*-

"""Forms to manipulate the columns."""
import re
from typing import Dict

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils.translation import ugettext_lazy as _
import pandas as pd

from ontask import is_legal_name, models
from ontask.core import DATE_TIME_WIDGET_OPTIONS
from ontask.dataops.pandas import is_unique_column, load_table

INITIAL_VALUE_LENGTH = 512

INTERVAL_PATTERN = '-?(?P<from>\\d+)\\s-\\s-?(?P<to>\\d+)'


class ColumnBasicForm(forms.ModelForm):
    """Basic form for column manipulation."""

    raw_categories = forms.CharField(
        strip=True,
        required=False,
        label=_('Comma separated list of values allowed in this column'))

    data_type_choices = [
        ('double', 'number'),
        ('integer', 'number'),
        ('string', 'string'),
        ('boolean', 'boolean'),
        ('datetime', 'datetime'),
    ]

    def __init__(self, *args, **kwargs):
        """Store the workflow and data frame."""
        self.workflow = kwargs.pop('workflow', None)
        self.data_frame = None
        self.allow_interval_as_initial = kwargs.pop(
            'allow_interval_as_initial',
            False)

        super().__init__(*args, **kwargs)

        # Remember the column name and position to perform content substitution
        if self.instance.name:
            self.old_name = self.instance.name
            self.old_position = self.instance.position

        self.fields['raw_categories'].initial = ', '.join(
            [str(cat) for cat in self.instance.get_categories()])

        self.fields['data_type'].choices = self.data_type_choices

        self.initial_valid_value = None

    def clean(self) -> Dict:
        """Check that the name is legal and the categories have right value."""
        form_data = super().clean()

        # Load the data frame from the DB for various checks and leave it in
        # the form for future use
        self.data_frame = load_table(
            self.workflow.get_data_frame_table_name())

        # Column name must be a legal variable name
        if 'name' in self.changed_data:
            # Name is legal
            msg = is_legal_name(form_data['name'])
            if msg:
                self.add_error('name', msg)
                return form_data

            # Check that the name is not present already
            if self.workflow.columns.filter(name=form_data['name']).exists():
                # New column name collides with existing one
                self.add_error(
                    'name',
                    _('There is a column already with this name'))
                return form_data

        # Categories must be valid types
        if 'raw_categories' in self.changed_data:
            if form_data['raw_categories']:
                # Condition 1: Values must be valid for the type of the column
                if self.allow_interval_as_initial and re.search(
                    INTERVAL_PATTERN,
                    form_data['raw_categories']
                ):
                    match = re.search(
                        INTERVAL_PATTERN,
                        form_data['raw_categories'])
                    from_val = int(match.group('from'))
                    to_val = int(match.group('to'))
                    if from_val > to_val:
                        tmp = from_val
                        from_val = to_val
                        to_val = tmp
                    category_values = [
                        str(val) for val in range(from_val, to_val + 1)]
                else:
                    category_values = [
                        cat.strip()
                        for cat in form_data['raw_categories'].split(',')]
                try:
                    valid_values = models.Column.validate_column_values(
                        form_data['data_type'],
                        category_values)
                except ValueError:
                    self.add_error(
                        'raw_categories',
                        _('Incorrect list of values'),
                    )
                    return form_data

                # Condition 2: The values in the dataframe column must be in
                # these categories (only if the column is being edited, though
                if self.instance.name and not all(
                    vval in valid_values
                    for vval in self.data_frame[self.instance.name]
                    if vval and not pd.isnull(vval)
                ):
                    self.add_error(
                        'raw_categories',
                        _(
                            'The values in the column are not compatible '
                            + ' with these ones.'))
                    return form_data
            else:
                valid_values = []

            self.instance.set_categories(valid_values)

        # Check the datetimes. One needs to be after the other
        a_from = self.cleaned_data.get('active_from')
        a_to = self.cleaned_data.get('active_to')
        if a_from and a_to and a_from >= a_to:
            self.add_error('active_from', _('Incorrect date/time window'))
            self.add_error('active_to', _('Incorrect date/time window'))

        # Check and force a correct column index
        ncols = self.workflow.columns.count()
        if form_data['position'] < 1 or form_data['position'] > ncols:
            form_data['position'] = ncols + 1

        return form_data

    class Meta:
        """Select model, fields and widget to consider."""

        model = models.Column
        fields = [
            'name',
            'description_text',
            'data_type',
            'position',
            'raw_categories',
            'active_from',
            'active_to']

        widgets = {
            'active_from': DateTimePickerInput(
                options=DATE_TIME_WIDGET_OPTIONS),
            'active_to': DateTimePickerInput(options=DATE_TIME_WIDGET_OPTIONS),
        }


class ColumnAddForm(ColumnBasicForm):
    """Form to add a regular column."""

    initial_value = forms.CharField(
        max_length=INITIAL_VALUE_LENGTH,
        strip=True,
        required=False,
        label=_('Value to assign to all cells in the column'))

    def __init__(self, *args, **kwargs):
        """Set the choices of the data type."""
        super().__init__(*args, **kwargs)

        self.fields['data_type'].choices = self.data_type_choices[1:]

    def clean(self) -> Dict:
        """Validate the initial value."""
        form_data = super().clean()

        # Try to convert the initial value ot the right type
        initial_value = form_data['initial_value']
        if initial_value:
            # See if the given value is allowed for the column data type
            try:
                self.initial_valid_value = models.Column.validate_column_value(
                    form_data['data_type'],
                    initial_value,
                )
            except ValueError:
                self.add_error(
                    'initial_value',
                    _('Incorrect initial value'),
                )

            categories = self.instance.get_categories()
            if categories and self.initial_valid_value not in categories:
                self.add_error(
                    'initial_value',
                    _('This value is not in the list of allowed values'),
                )

        return form_data

    class Meta(ColumnBasicForm.Meta):
        """Define fields to consider."""

        fields = [
            'name',
            'description_text',
            'data_type',
            'position',
            'active_from',
            'active_to']


class QuestionForm(ColumnBasicForm):
    """Form to add a question."""

    def __init__(self, *args, **kwargs):
        """Set the appropriate labels."""
        super().__init__(*args, **kwargs)

        self.fields['name'].label = _('Question name')
        self.fields['description_text'].label = _(
            'Description (shown to the learners)')
        self.fields['position'].label = _(
            'Question position (zero to insert last)')
        self.fields['active_from'].label = _('Question active from')
        self.fields['active_to'].label = _('Question active until')

        if self.instance.id is not None:
            self.fields['data_type'].disabled = True

    class Meta(ColumnBasicForm.Meta):
        """Set the fields."""

        fields = [
            'name',
            'description_text',
            'data_type',
            'position',
            'active_from',
            'active_to']


class CriterionForm(ColumnBasicForm):
    """Form to add a question."""

    def __init__(self, *args, **kwargs):
        """Adjust fields."""
        self.other_criterion = kwargs.pop('other_criterion')
        if self.other_criterion:
            self.other_criterion = self.other_criterion.column

        super().__init__(*args, **kwargs)

        self.fields['name'].label = _('Criterion name')
        self.fields['description_text'].label = _(
            'Criterion Description')

        if self.other_criterion:
            # Set and hide fields that have been defined.
            self.fields['raw_categories'].widget = forms.HiddenInput()
            self.fields['data_type'].initial = self.other_criterion.data_type
            self.fields['data_type'].widget = forms.HiddenInput()
        else:
            self.fields['raw_categories'].label = _(
                'Comma-separated list of levels of attainment')

    def clean(self) -> Dict:
        """Validate the position field."""
        form_data = super().clean()

        # Check and force a correct column index
        ncols = self.workflow.columns.count()
        if form_data['position'] < 1 or form_data['position'] > ncols:
            form_data['position'] = ncols + 1

        # Transfer categories from other column, or prevent being empty
        if self.other_criterion:
            self.instance.categories = self.other_criterion.categories
        elif not form_data['raw_categories']:
            self.add_error(
                'raw_categories',
                _('The criterion needs a non-empty set of values')
            )

        return form_data

    class Meta(ColumnBasicForm.Meta):
        """Set the fields."""

        fields = [
            'name',
            'description_text',
            'data_type',
            'position',
            'raw_categories']


class ColumnRenameForm(ColumnBasicForm):
    """Form to rename the form."""

    def __init__(self, *args, **kwargs):
        """Set the data type to disable to prevent type changes."""
        super().__init__(*args, **kwargs)

        self.fields['data_type'].disabled = True

    def clean(self) -> Dict:
        """Verify that the rename preserve key, or verify the unique prop."""
        form_data = super().clean()

        # Check if there has been a change in the 'is_key' status
        if 'is_key' in self.changed_data:
            # Case 1: True -> False If it is the only one, cannot be
            # allowed
            column_unique = self.instance.workflow.get_column_unique()
            if (
                self.instance.is_key
                and len([col for col in column_unique if col]) == 1
            ):
                self.add_error(
                    'is_key',
                    _('There must be at least one column with unique values'),
                )
                return form_data

            # Case 2: False -> True Unique values must be verified
            if (
                not self.instance.is_key
                and not is_unique_column(self.data_frame[self.instance.name])
            ):
                self.add_error(
                    'is_key',
                    _('The column does not have unique values for each row.'),
                )
                return form_data

        # Check and force a correct column index
        ncols = self.workflow.columns.count()
        if form_data['position'] < 1 or ncols < form_data['position']:
            form_data['position'] = ncols

        return form_data

    class Meta(ColumnBasicForm.Meta):
        """Select the fields."""

        fields = [
            'name',
            'description_text',
            'data_type',
            'position',
            'is_key',
            'active_from',
            'active_to']


class FormulaColumnAddForm(forms.ModelForm):
    """Form to get columns to combine and the operand to use."""

    columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label=_('Columns to combine*'))

    # Type of operation
    op_type = forms.ChoiceField(
        required=True,
        label='Operation')

    def __init__(self, form_data, *args, **kwargs):
        """Store the workflow columns and operands."""
        self.operands = kwargs.pop('operands')
        # Workflow columns
        self.wf_columns = kwargs.pop('columns')

        super().__init__(form_data, *args, **kwargs)

        # Populate the column choices
        self.fields['columns'].choices = [
            (idx, col.name) for idx, col in enumerate(self.wf_columns)
        ]

        # Populate the operand choices
        self.fields['op_type'].choices = [('', '---')] + [
            (op_name, op_value) for op_name, op_value, _ in self.operands]

        # Selected columns
        self.selected_columns = None

    def clean(self) -> Dict:
        """Verify that the data types of the selected columns are correct."""
        form_data = super().clean()

        if self.wf_columns.filter(name=form_data['name']).exists():
            self.add_error('name', _('A column with that name already exists'))
            return form_data

        # If there are no columns given, return
        column_idx_str = form_data.get('columns')
        if not column_idx_str:
            self.add_error(
                None,
                _('You need to select the columns to combine'),
            )
            return form_data

        # Get the list of columns selected in the form
        self.selected_columns = [
            self.wf_columns[int(idx)] for idx in column_idx_str]

        # Get the set of data types in the selected columns
        result_type = {col.data_type for col in self.selected_columns}

        # Get the operand
        operand = next(
            (op for op in self.operands if op[0] == form_data['op_type']),
            None)

        # The data type of the operand must be contained in the set of allowed
        if not result_type.issubset(set(operand[2])):
            self.add_error(
                None,
                _('Incorrect data type for the selected operand'),
            )
            return form_data

        # Check and force a correct column index
        ncols = self.wf_columns.count()
        if form_data['position'] < 1 or form_data['position'] > ncols:
            form_data['position'] = ncols + 1

        return form_data

    class Meta(ColumnBasicForm.Meta):
        """Set of fields to include in the form."""

        fields = [
            'name',
            'description_text',
            'position',
            'op_type',
            'columns',
            'active_from',
            'active_to']


class RandomColumnAddForm(ColumnBasicForm):
    """Form to create a column with random values."""

    def __init__(self, *args, **kwargs):
        """Modify the label of the raw_categories"""
        super().__init__(*args, **kwargs)

        self.fields['raw_categories'].label = _(
            'Number (values from 1 to N, interval m - n) '
            + 'or comma separated list of values.')


