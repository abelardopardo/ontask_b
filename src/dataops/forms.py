# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from django import forms

import ontask.ontask_prefs
from ontask.forms import RestrictedFileField
from .models import RowView

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___upload_'


def column_to_field(col, initial=None, required=False):
    """
    Function that given the description of a column it generates the
    appropriate field to be included in a form
    :param col: Column object to use as the basis to create the field
    :param initial: Initial value for the field
    :param required: flag to generate the field
    :return: Field object
    """

    if col.categories:
        # Column has a finite set of prefixed values
        choices = [(x, x) for x in col.categories]
        initial = next((v for x, v in enumerate(choices) if v[0] == initial),
                       ('', '---'))

        return forms.ChoiceField(choices,
                                 required=required,
                                 initial=initial,
                                 label=col.name)

    # Column is open value
    if col.data_type == 'string':
        if not initial:
            initial = ''
        if not col.categories:
            # The field does not have any categories
            return forms.CharField(initial=initial,
                                   label=col.name,
                                   required=required)

    elif col.data_type == 'integer':
        return forms.IntegerField(initial=initial,
                                  label=col.name,
                                  required=required)

    elif col.data_type == 'double':
        return forms.FloatField(initial=initial,
                                label=col.name,
                                required=required)

    elif col.data_type == 'boolean':
        return forms.BooleanField(initial=initial,
                                  label=col.name,
                                  required=required)

    elif col.data_type == 'datetime':
        return forms.DateTimeField(initial=initial,
                                   label=col.name,
                                   required=required)
    else:
        raise Exception('Unable to process datatype', col.data_type)


# Form to select columns
class SelectColumnForm(forms.Form):
    def __init__(self, *args, **kargs):
        """
        Kargs contain: columns: list of column objects, put_labels: boolean
        stating if the labels should be included in the form
        :param args:
        :param kargs:
        """
        # List of columns to process
        self.columns = kargs.pop('columns', [])

        # Should the labels be included?
        self.put_labels = kargs.pop('put_labels', False)

        super(SelectColumnForm, self).__init__(*args, **kargs)

        # Create as many fields as the given columns
        for i, c in enumerate(self.columns):
            # Include the labels if requested
            if self.put_labels:
                label = c.name
            else:
                label = ''

            self.fields['upload_%s' % i] = forms.BooleanField(
                label=label,
                required=False,
            )


# RowView manipulation form
class RowViewForm(forms.ModelForm):
    """
    Form to read information about a rowview. The required property of the
    filter field is set to False because it is enforced in the server.
    """

    def __init__(self, *args, **kwargs):
        super(RowViewForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['filter'].required = False

    class Meta:
        model = RowView
        fields = ('name', 'description_text', 'filter')


# Step 1 of the CSV upload
class UploadFileForm(forms.Form):
    file = RestrictedFileField(
        max_upload_size=str(ontask.ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask.ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label="",
        help_text='File in CSV format (typically produced by a statistics'
                  ' package or Excel)')


# Step 2 of the CSV upload
class SelectColumnUploadForm(SelectColumnForm):
    def __init__(self, *args, **kargs):

        super(SelectColumnUploadForm, self).__init__(*args, **kargs)

        # Create as new_name fields
        for i in range(len(self.columns)):
            self.fields['new_name_%s' % i] = forms.CharField(
                label='',
                strip=True,
                required=False
            )

    def clean(self):
        cleaned_data = super(SelectColumnUploadForm, self).clean()

        upload_list = [cleaned_data.get('upload_%s' % i, False)
                       for i in range(len(self.columns))]

        # Check if at least a unique column has been selected
        both_lists = zip(upload_list, self.columns)
        if not any([a and b for a, b in both_lists]):
            raise forms.ValidationError('No unique column specified',
                                        code='invalid')

        # Get list of new names
        new_names = [cleaned_data.get('new_name_%s' % i)
                     for i in range(len(self.columns))]

        # Check that there are no spaces in the names of the selected columns
        has_space = any([' ' in new_names[i]
                         for i, n in enumerate(upload_list) if n])
        if has_space:
            raise forms.ValidationError(
                'No spaces allowed in column names.',
                code='invalid')

        # Get the first illegal key name
        illegal_var_idx = ontask.find_ilegal_var(
            [n for x, n in enumerate(new_names) if upload_list[x]])
        if illegal_var_idx is not None:
            self.add_error(
                'new_name_%s' % illegal_var_idx[0],
                'Column names must start with a letter followed by '
                'letters, numbers or _.'
                'Value {0} is not allowed'.format(illegal_var_idx[1])
            )


# Step 3 of the CSV upload: select unique keys to merge
class SelectUniqueKeysForm(forms.Form):
    how_merge_choices = [('left', 'only the keys in the table'),
                         ('right', 'only the new keys'),
                         ('outer', 'the union of the table and new keys '
                                   '(outer)'),
                         ('inner', 'the intersection of the table and new'
                                   ' keys (inner)')]

    how_dup_columns_choices = [('override', 'override columns with new data'),
                               ('rename', 'be renamed and become new columns.')]

    dst_help = """This column is in the existing table and has values that 
    are unique for each row. This is one of the columns that will be used 
    to explore the upcoming data and match the rows."""

    src_help = """This column is in the table you are about to merge with 
    the table. It has a value that is unique for each row. It is suppose to
     have the same values as the Unique Column in Table. These two columns
    will be used to match the rows to merge the data with the existing
    table."""

    merge_help = """How the keys in the table and the file are used for the 
    merge: 1) If only the keys from the table are used, any row in the file 
    with a key value not in the table is removed (default). 2) If only the 
    keys from the file are used, any row in the table with a key value not 
    in the file is removed. 3) If the union of keys is used, no row is 
    removed, but some rows will have empty values. 4) If the intersection of 
    the keys is used, only those rows with keys in both the table and the 
    file will be updated, the rest will be deleted."""

    how_dup_columns_help = """The new data has columns with names identical 
    to those that are already part of the table. You may choose to override
    them with the new data, or rename the new data and add them as new 
    columns."""

    # common_help = """The data that is being loaded has column names that
    # are the same as the ones already existing. If you choose override, the
    # new columns will replace the old ones. If you choose rename, the new
    # columns will be renamed."""

    def __init__(self, *args, **kargs):
        # Get the dst choices
        dst_choices = [(x, x) for x in kargs.pop('dst_keys')]
        dst_selected_key = kargs.pop('dst_selected_key')
        dst_choice_initial = \
            next((v for x, v in enumerate(dst_choices)
                  if v[0] == dst_selected_key),
                 ('', '---'))

        # Get the src choices
        src_choices = [(x, x) for x in kargs.pop('src_keys')]
        src_selected_key = kargs.pop('src_selected_key')
        src_choice_initial = \
            next((v for x, v in enumerate(src_choices)
                  if v[0] == src_selected_key),
                 ('', '---'))

        how_merge = kargs.pop('how_merge', None)
        how_merge_initial = \
            next((v for x, v in enumerate(self.how_merge_choices)
                  if v[0] == how_merge),
                 None)

        # Boolean telling us if we have to add field to handle overlapping
        # column names
        are_overlap_cols = kargs.pop('are_overlap_cols')
        how_dup_columns = kargs.pop('how_dup_columns')

        super(SelectUniqueKeysForm, self).__init__(*args, **kargs)

        self.fields['dst_key'] = \
            forms.ChoiceField(initial=dst_choice_initial,
                              choices=dst_choices,
                              required=True,
                              label='Unique Key Column in Table',
                              help_text=self.dst_help)

        self.fields['src_key'] = \
            forms.ChoiceField(initial=src_choice_initial,
                              choices=src_choices,
                              required=True,
                              label='Unique Key Column in CSV',
                              help_text=self.src_help)

        self.fields['how_merge'] = \
            forms.ChoiceField(initial=how_merge_initial,
                              choices=self.how_merge_choices,
                              required=True,
                              label='Merge rows using',
                              help_text=self.merge_help)

        if are_overlap_cols:
            how_dup_columns_initial = \
                next((v for x, v in enumerate(self.how_dup_columns_choices)
                      if v[0] == how_dup_columns), None)
            self.fields['how_dup_columns'] = \
                forms.ChoiceField(initial=how_dup_columns_initial,
                                  choices=self.how_dup_columns_choices,
                                  required=True,
                                  label='Columns with already existing names'
                                        ' will',
                                  help_text=self.merge_help)


# Form to allow value selection through unique keys in a rowview
class RowViewDataSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):

        # Store the columns
        self.columns = kwargs.pop('columns')

        # Get the unique keys names and types
        self.key_cols = [x for x in self.columns if x.is_key]

        # Call the super constructor
        super(RowViewDataSearchForm, self).__init__(*args, **kwargs)

        for idx, col in enumerate(self.key_cols):
            self.fields[field_prefix + '%s' % idx] = column_to_field(col)


# Form to enter values in a row
class RowViewDataEntryForm(forms.Form):
    def __init__(self, *args, **kargs):

        # Store the instance
        self.columns = kargs.pop('columns', None)
        self.initial_values = kargs.pop('initial_values', None)

        super(RowViewDataEntryForm, self).__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.initial_values:
            self.initial_values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):
            self.fields[field_prefix + '%s' % idx] = \
                column_to_field(column, self.initial_values[idx])

            if column.is_key and self.initial_values[idx]:
                self.fields[field_prefix + '%s' % idx].widget.attrs[
                    'readonly'] = 'readonly'


# Form to allow value selection through unique keys in a workflow
class RowFilterForm(forms.Form):
    def __init__(self, *args, **kargs):

        # Store the instance
        self.workflow = kargs.pop('workflow')

        # Get the unique keys names and types
        columns = self.workflow.columns.all()

        self.key_names = [x.name for x in columns if x.is_key]
        self.key_types = [x.data_type for x in columns if x.is_key]

        super(RowFilterForm, self).__init__(*args, **kargs)

        for name, field_type in zip(self.key_names, self.key_types):
            if field_type == 'string':
                self.fields[name] = forms.CharField(initial='',
                                                    label=name,
                                                    required=False)
            elif field_type == 'integer':
                self.fields[name] = forms.IntegerField(label=name,
                                                       required=False)
            elif field_type == 'double':
                self.fields[name] = forms.FloatField(label=name,
                                                     required=False)
            elif field_type == 'boolean':
                self.fields[name] = forms.BooleanField(required=False,
                                                       label=name)
            elif field_type == 'datetime':
                self.fields[name] = forms.DateTimeField(required=False,
                                                        label=name)
            else:
                raise Exception('Unable to process datatype', field_type)


# Form to enter values in a row
class RowForm(forms.Form):
    def __init__(self, *args, **kargs):

        # Store the instance
        self.workflow = kargs.pop('workflow', None)
        self.initial_values = kargs.pop('initial_values', None)

        super(RowForm, self).__init__(*args, **kargs)

        if not self.workflow:
            return

        # Get the columns
        self.columns = self.workflow.get_columns()

        # If no initial values have been given, replicate a list of Nones
        if not self.initial_values:
            self.initial_values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):
            field_name = field_prefix + '%s' % idx
            self.fields[field_name] = \
                column_to_field(column, self.initial_values[idx])

            if column.is_key and self.initial_values[idx]:
                self.fields[field_name].widget.attrs['readonly'] = 'readonly'
