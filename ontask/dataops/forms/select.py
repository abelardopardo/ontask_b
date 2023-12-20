"""Forms to select the columns for upload and decide which keys to keep."""
from typing import Dict

from django import forms
from django.utils.translation import gettext_lazy as _


class MergeForm(forms.Form):
    """Form to choose the merge method for data frames."""

    how_merge_choices = [
        ('', _('- Choose row selection method -')),
        ('outer', _('1) Select all rows in both the existing and new table')),
        ('inner', _(
            '2) Select only the rows with keys present in both the '
            + 'existing and new table')),
        ('left', _('3) Select only the rows with keys in the existing table')),
        ('right', _('4) Select only the rows with keys in the new table')),
    ]

    merge_help = _('Select one method to see detailed information')

    how_merge_initial = None

    def __init__(self, *args, **kargs):
        """Adjust the choices for the select fields."""
        given_how = kargs.pop('how_merge', None)
        self.how_merge_initial = next((
            mrg for mrg in self.how_merge_choices if given_how == mrg[0]),
            None)

        super().__init__(*args, **kargs)

        self.fields['how_merge'] = forms.ChoiceField(
            initial=self.how_merge_initial,
            choices=self.how_merge_choices,
            required=True,
            label=_('Method to select rows to merge'),
            help_text=self.merge_help)


class SelectColumnUploadForm(forms.Form):
    """Form to handle the selection of columns when uploading."""

    def __init__(self, *args, **kargs):
        """Initialize the fields for the given columns.

        Kargs contain:
          column_names: list with names of the columns to upload,
          is_key: list stating if the corresponding column is key

        :param args:
        :param kargs: Multiple additional parameters to store.
        """
        # Names of the columns to process and Boolean stating if they are key
        self.column_names = kargs.pop('column_names')
        self.columns_to_upload = kargs.pop('columns_to_upload')
        self.is_key = kargs.pop('is_key')
        self.keep_key = kargs.pop('keep_key')

        super().__init__(*args, **kargs)

        # Create as many fields as the given columns
        col_info = zip(self.column_names, self.columns_to_upload)
        for idx, (colname, upload) in enumerate(col_info):
            self.fields['upload_%s' % idx] = forms.BooleanField(
                initial=upload,
                label='',
                required=False)

            self.fields['new_name_%s' % idx] = forms.CharField(
                initial=colname,
                label='',
                strip=True,
                required=False)

            # Field to confirm if the key columns are kept.
            if self.is_key[idx]:
                self.fields['make_key_%s' % idx] = forms.BooleanField(
                    initial=self.keep_key[idx],
                    label='',
                    required=False)

    def clean(self) -> Dict:
        """Check that at least a key column has been selected."""
        cleaned_data = super().clean()

        field_info = zip(
            [
                cleaned_data.get('upload_%s' % idx)
                for idx in range(len(self.column_names))
            ],
            self.is_key,
            [
                cleaned_data.get('make_key_%s' % idx)
                for idx in range(len(self.column_names))
            ],
        )

        # Check if at least a unique column has been selected
        no_key = not any(all(triplet) for triplet in field_info)
        if no_key:
            self.add_error(
                None,
                _('No unique column specified'))

        return cleaned_data


class SelectKeysForm(MergeForm):
    """Form to select the keys for merging."""

    dst_help = _(
        'Key column in the existing table to match with the new table.')

    src_help = _(
        'Key column in the new table to match with the existing table.')

    def __init__(self, *args, **kargs):
        """Adjust the choices for the select fields."""
        # Get the dst choices
        selected_key = kargs.pop('dst_selected_key')
        dst_choices = [(dkey, dkey) for dkey in kargs.pop('dst_keys')]
        dst_choice_initial = next((
            skey for skey in dst_choices
            if skey[0] == selected_key),
            ('', '---'))

        # Get the src choices
        selected_key = kargs.pop('src_selected_key')
        src_choices = [(skey, skey) for skey in kargs.pop('src_keys')]
        src_choice_initial = next((
            skey for skey in src_choices
            if selected_key == skey[0]),
            ('', _('- Select merge option -')))

        super().__init__(*args, **kargs)

        self.fields['dst_key'] = forms.ChoiceField(
            initial=dst_choice_initial,
            choices=dst_choices,
            required=True,
            label=_('Key Column in Existing Table'),
            help_text=self.dst_help)

        self.fields['src_key'] = forms.ChoiceField(
            initial=src_choice_initial,
            choices=src_choices,
            required=True,
            label=_('Key Column in New Table'),
            help_text=self.src_help)

        self.order_fields(['dst_key', 'src_key', 'how_merge'])
