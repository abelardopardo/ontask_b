# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from django import forms

import ontask.ontask_prefs
from ontask.forms import RestrictedFileField, column_to_field

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___upload_'


# Step 1 of the CSV upload
class UploadCSVFileForm(forms.Form):
    """
    Form to read a csv file. It also allows to specify the number of lines to
    skip at the top and the bottom of the file. This functionality is offered
    by the underlyng function read_csv in Pandas
    """
    file = RestrictedFileField(
        max_upload_size=str(ontask.ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask.ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label="",
        help_text='File in CSV format (typically produced by a statistics'
                  ' package or Excel)')

    skip_lines_at_top = forms.IntegerField(
        label='Lines to skip at the top',
        help_text="Number of lines to skip at the top when reading the file",
        initial=0,
        required=False
    )

    skip_lines_at_bottom = forms.IntegerField(
        label='Lines to skip at the bottom',
        help_text="Number of lines to skip at the bottom when reading the "
                  "file",
        initial=0,
        required=False
    )

    def clean(self, *args, **kwargs):
        """
        Function to check that the integers are positive.
        :return: The cleaned data
        """

        data = super(UploadCSVFileForm, self).clean(*args, **kwargs)

        if data['skip_lines_at_top'] < 0:
            self.add_error(
                'skip_lines_at_top',
                'This number has to be zero or positive'
            )

        if data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                'This number has to be zero or positive'
            )

        return data


# Step 1 of the CSV upload
class UploadExcelFileForm(forms.Form):
    """
    Form to read an Excel file.
    """
    file = RestrictedFileField(
        max_upload_size=str(ontask.ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        allow_empty_file=False,
        label="",
        help_text='File in Excel format (.xls or .xlsx)')

    sheet = forms.CharField(max_length=512,
                            required=True,
                            initial='Sheet 1')


# Step 1 of the CSV upload
class UploadSQLForm(forms.Form):
    """
    Form to read data from SQL. We collect information to create a Database URI
    to be used by SQLAlchemy:

    dialect[+driver]://user:password@host/dbname[?key=value..]
    """

    dialect = forms.CharField(
        label='Dialect',
        max_length=512,
        required=True,
        initial='',
        help_text='Database type (mysql, oracle, postgresql, etc.'
    )

    driver = forms.CharField(
        label='Driver',
        max_length=512,
        required=False,
        initial='',
        help_text='Name of the driver implementing the DBAPI'
    )

    dbusername = forms.CharField(
        max_length=512,
        label="Database user name",
        required=False,
        initial='',
        help_text='User name to connect'
    )

    dbpassword = forms.CharField(
        label='Database password',
        required=False,
        widget=forms.PasswordInput
    )

    host = forms.CharField(
        label='Host',
        max_length=512,
        required=True,
        help_text='Host to connect (include port if needed)'
    )

    dbname = forms.CharField(
        label='Database name',
        max_length=512,
        required=True,
        help_text='Name of the database'
    )

    query = forms.CharField(
        label='Query',
        required=True,
        widget=forms.Textarea,
        help_text='SQL query or table name to read'
    )

# Form to select columns to upload and rename
class SelectColumnUploadForm(forms.Form):

    def __init__(self, *args, **kargs):
        """
        Kargs contain:
          column_names: list with names of the columns to upload,
          is_key: list stating if the corresponding column is key
        :param args:
        :param kargs:
        """

        # Names of the columns to process and Boolean stating if they are key
        self.column_names = kargs.pop('column_names')
        self.is_key = kargs.pop('is_key')

        super(SelectColumnUploadForm, self).__init__(*args, **kargs)

        # Create as many fields as the given columns
        for idx, c in enumerate(self.column_names):
            self.fields['upload_%s' % idx] = forms.BooleanField(
                label='',
                required=False,
            )

            self.fields['new_name_%s' % idx] = forms.CharField(
                initial=c,
                label='',
                strip=True,
                required=False
            )

    def clean(self):
        cleaned_data = super(SelectColumnUploadForm, self).clean()

        upload_list = [cleaned_data.get('upload_%s' % i, False)
                       for i in range(len(self.column_names))]

        # Check if at least a unique column has been selected
        both_lists = zip(upload_list, self.is_key)
        if not any([a and b for a, b in both_lists]):
            raise forms.ValidationError('No unique column specified',
                                        code='invalid')

        # Get list of new names
        new_names = [cleaned_data.get('new_name_%s' % i)
                     for i in range(len(self.column_names))]


# Step 3 of the CSV upload: select unique keys to merge
class SelectKeysForm(forms.Form):
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
     have the same values as the Key Column in Table. These two columns
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

        super(SelectKeysForm, self).__init__(*args, **kargs)

        self.fields['dst_key'] = \
            forms.ChoiceField(initial=dst_choice_initial,
                              choices=dst_choices,
                              required=True,
                              label='Key Column in Table',
                              help_text=self.dst_help)

        self.fields['src_key'] = \
            forms.ChoiceField(initial=src_choice_initial,
                              choices=src_choices,
                              required=True,
                              label='Key Column in CSV',
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
