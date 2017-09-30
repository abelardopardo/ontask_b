# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

import ontask
from . import settings


class RestrictedFileField(forms.FileField):

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = str(settings.MAX_UPLOAD_SIZE)
        super(RestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedFileField, self).clean(*args, **kwargs)
        try:
            if data.content_type in self.content_types:
                if data.size > self.max_upload_size:
                    raise forms.ValidationError(
                        _('File size must be under %s. Current file size is'
                          ' %s.')
                        % (filesizeformat(self.max_upload_size),
                           filesizeformat(data.size)))
            else:
                raise forms.ValidationError(
                    _('File type (%s) is not supported.') % data.content_type)
        except AttributeError:
            pass

        return data


# Step 1 of the CSV upload
class UploadFileForm(forms.Form):
    file = RestrictedFileField(
        max_upload_size=str(settings.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(settings.CONTENT_TYPES)),
        allow_empty_file=False,
        label="",
        help_text='File in CSV format (typically produced by a statistics'
                  ' package or Excel)')


# Step 2 of the CSV upload
class SelectColumnForm(forms.Form):

    def __init__(self, *args, **kargs):

        self.unique_columns = kargs.pop('unique_columns')

        super(SelectColumnForm, self).__init__(*args, **kargs)

        # Create as many fields as twice the number of columns
        for i in range(len(self.unique_columns)):
            self.fields['upload_%s' % i] = forms.BooleanField(
                label='',
                required=False,
            )
            self.fields['new_name_%s' % i] = forms.CharField(
                label='',
                strip=True,
                required=False
            )

    def clean(self):
        cleaned_data = super(SelectColumnForm, self).clean()

        upload_list = [cleaned_data.get('upload_%s' % i, False)
                       for i in range(len(self.unique_columns))]

        # Check if at least a unique column has been selected
        both_lists = zip(upload_list, self.unique_columns)
        if not any([a and b for a, b in both_lists]):
            raise forms.ValidationError('No unique column specified',
                                        code='invalid')

        # Get list of new names
        new_names = [cleaned_data.get('new_name_%s' % i)
                     for i in range(len(self.unique_columns))]

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
                'Column names must start with letter or _ followed by letters,'
                'numbers or _. '
                'Value {0} is not allowed'.format(illegal_var_idx[1])
            )



# Step 3 of the CSV upload: select unique keys to merge
class SelectUniqueKeysForm(forms.Form):

    how_merge_choices = [('left', 'only the keys in the matrix'),
                         ('right', 'only the new keys'),
                         ('outer', 'the union of the matrix and new keys '
                                   '(outer)'),
                         ('inner', 'the intersection of the matrix and new'
                                   ' keys (inner)')]

    how_dup_columns_choices = [('override', 'override columns with new data'),
                               ('rename', 'be renamed and become new columns.')]

    dst_help = """This column is in the existing matrix and has values that 
    are unique for each row. This is one of the columns that will be used 
    to explore the upcoming data and match the rows."""

    src_help = """This column is in the table you are about to merge with 
    the matrix. It has a value that is unique for each row. It is suppose to
     have the same values as the Unique Column in Matrix. These two columns
    will be used to match the rows to merge the data with the existing
    matrix."""

    merge_help = """How the keys in the matrix and the file are used for the 
    merge: 1) If only the keys from the matrix are used, any row in the file 
    with a key value not in the matrix is removed (default). 2) If only the 
    keys from the file are used, any row in the matrix with a key value not 
    in the file is removed. 3) If the union of keys is used, no row is 
    removed, but some rows will have empty values. 4) If the intersection of 
    the keys is used, only those rows with keys in both the matrix and the 
    file will be updated, the rest will be deleted."""

    how_dup_columns_help = """The new data has columns with names identical 
    to those that are already part of the matrix. You may choose to override
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
                              label='Unique Key Column in Matrix',
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
