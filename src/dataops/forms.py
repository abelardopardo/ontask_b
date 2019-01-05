# -*- coding: utf-8 -*-


import json
from builtins import next
from builtins import object
from builtins import range
from builtins import str
from builtins import zip

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _

import ontask.ontask_prefs
from dataops.models import SQLConnection
from ontask.forms import (
    RestrictedFileField, column_to_field,
    dateTimeWidgetOptions
)

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___upload_'


# Form to select a subset of the columns
class PluginInfoForm(forms.Form):
    """
    Form to select a subset of columns
    """

    # Columns to combine
    columns = forms.ModelMultipleChoiceField(
        label=_('Input Columns (to read data)'),
        queryset=None,
        required=False,
        help_text=_('To select a subset of the table to pass to the plugin'))

    def __init__(self, *args, **kwargs):
        self.workflow = kwargs.pop('workflow', None)
        self.plugin_instance = kwargs.pop('plugin_instance', None)

        super(PluginInfoForm, self).__init__(*args, **kwargs)

        if self.plugin_instance.input_column_names != []:
            # The set of columns is fixed, remove the field.
            self.fields.pop('columns')
        else:
            # The queryset for the columns must be extracted from the
            # workflow and should only include the non-key columns
            self.fields['columns'].queryset = self.workflow.columns.filter(
                is_key=False
            )

        # Field to choose the Key column to merge the results
        self.fields['merge_key'] = forms.ChoiceField(
            initial=('', '---'),
            label=_('Key column for merging'),
            required=True,
            help_text=_('One of the existing key columns to merge the '
                        'results'),
            choices=[('', '---')] + [(x, x) for x in
                                     self.workflow.columns.filter(is_key=True)]
        )

        # Add the fields for the output column names
        for idx, cname in enumerate(self.plugin_instance.output_column_names):
            self.fields[field_prefix + 'output_%s' % idx] = forms.CharField(
                initial=cname,
                label=_('Name for result column "{0}"').format(cname),
                strip=True,
                required=False,
            )

        self.fields['out_column_suffix'] = forms.CharField(
            initial='',
            label=_('Suffix to add to result columns (empty to ignore)'),
            strip=True,
            required=False,
            help_text=
            _('Added to all output column names. Useful to keep results from '
              'several executions in separated columns.')
        )

        for idx, (k, p_type, p_allow, p_init, p_help) in \
                enumerate(self.plugin_instance.parameters):

            if p_allow:
                new_field = forms.ChoiceField(
                    choices=[(x, x) for x in p_allow],
                    required=False,
                    label=k,
                    help_text=p_help)
            elif p_type == 'integer':
                new_field = forms.IntegerField(
                    label=k,
                    required=False,
                    help_text=p_help
                )
            elif p_type == 'double':
                new_field = forms.FloatField(
                    label=k,
                    required=False,
                    help_text=p_help
                )
            elif p_type == 'string':
                new_field = forms.CharField(
                    max_length=1024,
                    strip=True,
                    required=False,
                    label=k,
                    help_text=p_help
                )
            elif p_type == 'boolean':
                new_field = forms.BooleanField(
                    required=False,
                    label=k,
                    help_text=p_help
                )
            else:  # p_type == 'datetime':
                new_field = forms.DateTimeField(
                    required=False,
                    label=k,
                    widget=DateTimePickerInput(options=dateTimeWidgetOptions),
                    help_text=p_help
                )

            # Set the initial value of each field
            if p_allow:
                new_field.initial = (p_init, p_init)
            else:
                if p_type == 'datetime':
                    new_field.initial = parse_datetime(p_init)
                else:
                    new_field.initial = p_init

            # Insert the new_field in the form
            self.fields[field_prefix + 'parameter_%s' % idx] = new_field

    def clean(self):

        data = super(PluginInfoForm, self).clean()

        columns = data.get('columns', None)
        if columns and columns.count() == 0:
            self.add_error(
                'columns',
                _('The plugin needs at least one input column')
            )

        return data


# Step 1 of the CSV upload
class UploadCSVFileForm(forms.Form):
    """
    Form to read a csv file. It also allows to specify the number of lines to
    skip at the top and the bottom of the file. This functionality is offered
    by the underlyng function read_csv in Pandas
    """
    file = RestrictedFileField(
        max_upload_size=int(ontask.ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask.ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label="",
        help_text=_('File in CSV format (typically produced by a statistics'
                    ' package or Excel)'))

    skip_lines_at_top = forms.IntegerField(
        label=_('Lines to skip at the top'),
        help_text=_("Number of lines to skip at the top when reading the "
                    "file"),
        initial=0,
        required=False
    )

    skip_lines_at_bottom = forms.IntegerField(
        label=_('Lines to skip at the bottom'),
        help_text=_("Number of lines to skip at the bottom when reading the "
                    "file"),
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
                _('This number has to be zero or positive')
            )

        if data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                _('This number has to be zero or positive')
            )

        return data


# Step 1 of the CSV upload
class UploadExcelFileForm(forms.Form):
    """
    Form to read an Excel file.
    """
    file = RestrictedFileField(
        max_upload_size=int(ontask.ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        allow_empty_file=False,
        label="",
        help_text=_('File in Excel format (.xls or .xlsx)'))

    sheet = forms.CharField(
        max_length=512,
        required=True,
        initial='',
        help_text=_('Sheet within the excelsheet to upload'))


# Step 1 of the CSV upload
class UploadGoogleSheetForm(forms.Form):
    """
    Form to read a Google Sheet file through a URL. It also allows to specify
    the number of lines to skip at the top and the bottom of the file. This
    functionality is offered by the underlyng function read_csv in Pandas
    """

    google_url = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('URL'),
        help_text=_('URL to access the Google Spreadsheet in CSV format')
    )

    skip_lines_at_top = forms.IntegerField(
        label=_('Lines to skip at the top'),
        help_text=_("Number of lines to skip at the top when reading the "
                    "file"),
        initial=0,
        required=False
    )

    skip_lines_at_bottom = forms.IntegerField(
        label=_('Lines to skip at the bottom'),
        help_text=_("Number of lines to skip at the bottom when reading the "
                    "file"),
        initial=0,
        required=False
    )

    def clean(self, *args, **kwargs):
        """
        Function to check that the integers are positive.
        :return: The cleaned data
        """

        data = super(UploadGoogleSheetForm, self).clean(*args, **kwargs)

        if data['skip_lines_at_top'] < 0:
            self.add_error(
                'skip_lines_at_top',
                _('This number has to be zero or positive')
            )

        if data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                _('This number has to be zero or positive')
            )

        return data


class SQLConnectionForm(forms.ModelForm):
    """
    Form to read data from SQL. We collect information to create a Database URI
    to be used by SQLAlchemy:

    dialect[+driver]://user:password@host/dbname[?key=value..]
    """

    class Meta(object):
        model = SQLConnection

        fields = [
            'name',
            'description_txt',
            'conn_type',
            'conn_driver',
            'db_user',
            'db_password',
            'db_host',
            'db_port',
            'db_name',
            'db_table'
        ]


# Step 1 of the CSV upload
class SQLRequestPassword(forms.Form):
    """
    Form to ask for a password for a SQL connection execution
    """

    password = forms.CharField(
        max_length=2048,
        widget=forms.PasswordInput,
        required=True,
        help_text=_('Password to authenticate the database connection'))


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
        self.columns_to_upload = kargs.pop('columns_to_upload')
        self.is_key = kargs.pop('is_key')
        self.keep_key = kargs.pop('keep_key')

        super(SelectColumnUploadForm, self).__init__(*args, **kargs)

        # Create as many fields as the given columns
        for idx, (c, upload) in enumerate(zip(self.column_names,
                                              self.columns_to_upload)):
            self.fields['upload_%s' % idx] = forms.BooleanField(
                initial=upload,
                label='',
                required=False,
            )

            self.fields['new_name_%s' % idx] = forms.CharField(
                initial=c,
                label='',
                strip=True,
                required=False
            )

            # Field to confirm if the key columns are kept.
            if self.is_key[idx]:
                self.fields['make_key_%s' % idx] = forms.BooleanField(
                    initial=self.keep_key[idx],
                    label='',
                    required=False
                )

    def clean(self):
        cleaned_data = super(SelectColumnUploadForm, self).clean()

        upload_list = [cleaned_data.get('upload_%s' % i, False)
                       for i in range(len(self.column_names))]
        keep_key = [cleaned_data.get('make_key_%s' % i, False)
                    for i in range(len(self.column_names))]

        # Check if at least a unique column has been selected
        if not any([a and b and c
                    for a, b, c in zip(upload_list, self.is_key, keep_key)]):
            raise forms.ValidationError(_('No unique column specified'),
                                        code='invalid')


# Step 3 of the CSV upload: select unique keys to merge
class SelectKeysForm(forms.Form):
    how_merge_choices = [
        ('', _('- Choose row selection method -')),
        ('outer', _('1) Select all rows in both the existing and new table')),
        ('inner', _('2) Select only the rows with keys present in both the '
                    'existing and new table')),
        ('left', _('3) Select only the rows with keys in the existing table')),
        ('right', _('4) Select only the rows with keys in the new table')),
    ]

    dst_help = _("Key column in the existing table to match with the new "
                 "table.")

    src_help = _("Key column in the new table to match with the existing "
                 "table.")

    merge_help = _("Select one method to see detailed information")

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
                 ('', _('- Select merge option -')))

        how_merge = kargs.pop('how_merge', None)
        how_merge_initial = \
            next((v for x, v in enumerate(self.how_merge_choices)
                  if v[0] == how_merge),
                 None)

        super(SelectKeysForm, self).__init__(*args, **kargs)

        self.fields['dst_key'] = \
            forms.ChoiceField(initial=dst_choice_initial,
                              choices=dst_choices,
                              required=True,
                              label=_('Key Column in Existing Table'),
                              help_text=self.dst_help)

        self.fields['src_key'] = \
            forms.ChoiceField(initial=src_choice_initial,
                              choices=src_choices,
                              required=True,
                              label=_('Key Column in New Table'),
                              help_text=self.src_help)

        self.fields['how_merge'] = \
            forms.ChoiceField(initial=how_merge_initial,
                              choices=self.how_merge_choices,
                              required=True,
                              label=_('Method to select rows to merge/update'),
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
                raise Exception(_('Unable to process datatype'), field_type)


class RowForm(forms.Form):
    """
    Form to enter values for a table row
    """

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

            if column.is_key:
                if self.initial_values[idx]:
                    self.fields[field_name].widget.attrs['readonly'] = \
                        'readonly'
                else:
                    self.fields[field_name].required = True
            elif column.data_type == 'integer':
                self.fields[field_name].required = True
