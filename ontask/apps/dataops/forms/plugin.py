# -*- coding: utf-8 -*-

"""Form to collect information to run a plugin."""

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext, ugettext_lazy as _

from dataops.forms.upload import FIELD_PREFIX
from ontask.forms import date_time_widget_options

STRING_PARAM_MAX_LENGTH = 1024


class PluginInfoForm(forms.Form):
    """Form to select a subset of columns."""

    # Columns to combine
    columns = forms.ModelMultipleChoiceField(
        label=_('Input Columns (to read data)'),
        queryset=None,
        required=False,
        help_text=_('To select a subset of the table to pass to the plugin'))

    def _create_datatype_field(self, p_type, p_help, lbl):
        """Create a new field depending on the datatype."""
        if p_type == 'integer':
            new_field = forms.IntegerField(
                label=lbl,
                required=False,
                help_text=p_help)

        elif p_type == 'double':
            new_field = forms.FloatField(
                label=lbl,
                required=False,
                help_text=p_help)

        elif p_type == 'string':
            new_field = forms.CharField(
                max_length=STRING_PARAM_MAX_LENGTH,
                strip=True,
                required=False,
                label=lbl,
                help_text=p_help)
        elif p_type == 'boolean':
            new_field = forms.BooleanField(
                required=False,
                label=lbl,
                help_text=p_help)
        else:  # p_type == 'datetime':
            new_field = forms.DateTimeField(
                required=False,
                label=lbl,
                widget=DateTimePickerInput(options=date_time_widget_options),
                help_text=p_help)

        return new_field

    def _create_output_column_fields(self):
        """Create the fields for the outputs and the output suffix."""
        for idx, cname in enumerate(self.plugin_instance.output_column_names):
            self.fields[FIELD_PREFIX + 'output_%s' % idx] = forms.CharField(
                initial=cname,
                label=ugettext('Name for result column "{0}"').format(cname),
                strip=True,
                required=False)

        self.fields['out_column_suffix'] = forms.CharField(
            initial='',
            label=_('Suffix to add to result columns (empty to ignore)'),
            strip=True,
            required=False,
            help_text=_(
                'Added to all output column names. '
                + 'Useful to keep results from '
                + 'several executions in separated columns.'))

    def _create_param_fields(self):
        """Create the fields to capture the parameters."""
        for idx, (lbl, p_type, p_allow, p_init, p_help) in enumerate(
            self.plugin_instance.parameters,
        ):

            if p_allow:
                new_field = forms.ChoiceField(
                    choices=[(cval, cval) for cval in p_allow],
                    required=False,
                    label=lbl,
                    help_text=p_help)
            else:
                new_field = self._create_datatype_field(p_type, p_help, lbl)

            # Set the initial value of each field
            if p_allow:
                new_field.initial = (p_init, p_init)
            else:
                if p_type == 'datetime':
                    new_field.initial = parse_datetime(p_init)
                else:
                    new_field.initial = p_init

            # Insert the new_field in the form
            self.fields[FIELD_PREFIX + 'parameter_%s' % idx] = new_field

    def __init__(self, *args, **kwargs):
        """Create the form based on the columns and the plugin information."""
        self.workflow = kwargs.pop('workflow', None)
        self.plugin_instance = kwargs.pop('plugin_instance', None)

        super().__init__(*args, **kwargs)

        if self.plugin_instance.input_column_names:
            # The set of columns is fixed, remove the field.
            self.fields.pop('columns')

            # Create the fields of type select to map the inputs in the plugin
            # to the names in the workflow columns. We will allow them to be
            # empty
            for idx, icolumn in enumerate(
                self.plugin_instance.input_column_names,
            ):
                field_name = FIELD_PREFIX + 'input_%s' % idx
                choices = [
                    (col.id, col.name) for col in self.workflow.columns.all()]
                choices.insert(0, ('', _('Select column')))
                self.fields[field_name] = forms.ChoiceField(
                    initial=('', _('Select column')),
                    label=_('Column for input {0}').format(icolumn),
                    required=True,
                    choices=choices)
        else:
            # The plugin allows for an arbitrary set of columns to be selected.
            # The queryset for the columns must be extracted from the
            # workflow
            self.fields['columns'].queryset = self.workflow.columns.all()

        # Field to choose the Key column to merge the results
        self.fields['merge_key'] = forms.ChoiceField(
            initial=('', '---'),
            label=_('Key column for merging'),
            required=True,
            help_text=_(
                'One of the existing key columns to merge the '
                + 'results'),
            choices=[('', '---')] + [
                (col, col) for col in
                self.workflow.columns.filter(is_key=True)])

        self._create_output_column_fields()

        self._create_param_fields()

    def clean(self):
        """Validate that input and output lists."""
        form_data = super().clean()

        # Input columns need to be non-empty
        columns = form_data.get('columns')
        if columns and columns.count() == 0:
            self.add_error(
                'columns',
                _('The plugin needs at least one input column'),
            )

        # Output columns cannot have the same name as any key columns
        # (otherwise they will collide in the final merge)
        if self.workflow.columns.filter(name__in=[]).exists():
            self.add_error(
                None,
                'Output name cannot be the same as key column. Please change',
            )

        return form_data
