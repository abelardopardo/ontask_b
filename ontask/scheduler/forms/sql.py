# -*- coding: utf-8 -*-

"""Forms required to schedule SQL upload/merge operation"""
from typing import Dict

from django import forms
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.dataops import forms as dataops_forms
from ontask.scheduler.forms import ScheduleBasicForm


class ScheduleSQLUploadForm(
    ScheduleBasicForm,
    dataops_forms.MergeForm,
    dataops_forms.SQLRequestConnectionParam):
    """Form to request info for the SQL scheduled upload

    Three blocks of information are requested:

    Block 1: Name, description, start -- frequency -- stop times

    Block 2: Parameters for the SQL connection

    Block 3: Parameters for the merge: Left/Right column + merge method
    """

    dst_help = dataops_forms.SelectKeysForm.dst_help

    dst_key = forms.ChoiceField(
        required=True,
        label=_('Key Column in Existing Table'),
        help_text=dst_help)

    src_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        strip=True,
        required=True,
        label=_('Key column in new data'))

    def __init__(self, *args, **kargs):
        """Initalize all the fields"""
        dst_choices = [(dkey, dkey) for dkey in kargs.pop('columns')]

        super().__init__(*args, **kargs)

        self.set_fields_from_dict(['dst_key', 'src_key', 'how_merge'])

        self.fields['dst_key'].choices = dst_choices

    def clean(self) -> Dict:
        """Store the fields in the Form Payload"""
        form_data = super().clean()
        self.store_fields_in_dict([
            ('dst_key', None),
            ('src_key', None),
            ('how_merge', None)])

        return form_data
