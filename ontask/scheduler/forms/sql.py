# -*- coding: utf-8 -*-

"""Forms required to schedule SQL upload/merge operation"""
from typing import Dict

from django import forms
from django.utils.translation import gettext_lazy as _

from ontask import models
import ontask.connection.forms
from ontask.dataops import forms as dataops_forms
from ontask.scheduler.forms import ScheduleBasicForm


class ScheduleSQLUploadForm(
    ScheduleBasicForm,
    dataops_forms.MergeForm,
    ontask.connection.forms.SQLRequestConnectionParam
):
    """Form to request info for the SQL scheduled upload

    Three blocks of information are requested:

    Block 1: Name, description, start -- frequency -- stop times

    Block 2: Parameters for the SQL connection

    Block 3: Parameters for the merge: Left/Right column + merge method
    """

    dst_help = dataops_forms.SelectKeysForm.dst_help

    dst_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        strip=True,
        required=False,
        label=_('Key column in the existing table. '
                'Leave empty if uploading to empty workflow'),
        help_text=dst_help)

    src_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        strip=True,
        required=False,
        label=_('Key column in new table. '
                'Leave empty if uploading to empty workflow'))

    def __init__(self, *args, **kwargs):
        """Initialize all the fields"""
        super().__init__(*args, **kwargs)
        self.set_fields_from_dict(['dst_key', 'src_key', 'how_merge'])

        self.fields['how_merge'].required = False

    def clean(self) -> Dict:
        """Store the fields in the Form Payload"""
        form_data = super().clean()
        self.store_fields_in_dict([
            ('dst_key', None),
            ('src_key', None),
            ('how_merge', None)])

        # If the workflow has data, both keys have to be non empty, the
        # first one needs to be a unique column, and the merge method cannot
        # be empty
        if self.workflow.has_data_frame():
            if not form_data['dst_key'] or not form_data['src_key']:
                self.add_error(
                    None,
                    _('The operation requires the names of two key columns.')
                )
            column = self.workflow.columns.filter(
                name=form_data['dst_key']).filter(is_key=True).first()
            if form_data['dst_key'] and not column:
                self.add_error(
                    'dst_key',
                    _('The column selected is not a key column.')
                )
            if not form_data['how_merge']:
                self.add_error(
                    'how_merge',
                    _('The operation requires a merge method.')
                )
        return form_data
