# -*- coding: utf-8 -*-

"""Forms to process action execution.

1) ExportWokflowBase: export workflow boolean field

2) EmailSubjectFormBase; subject

3) EmailCCBCCFormBase: cc and bcc for email

4) ItemColumnConfirm: item_column and confirm_items

5) JSONTokenForm: Token

6) EmailActionForm: 2 + 3 + 4 + send_confirmation, track_read

7) EmailActionRunForm: 6 + 1

8) SendListActionForm: 2 + 3 + email_to

9) SendListActionRunForm: 8 + 1

10) ZipActionRunForm: 1 + 4 + user_fname_column, file_suffix, zip_for_moodle

11) CanvasEmailActionForm: 2 + 4 (target_url dynamically added)

12) CanvasEmailActionRunForm: 11 + 1

13) JSONActionForm: 4, 5

14) JSONActionRunForm: 13 + 1

15) JSONListActionForm: 5

16) JSONListActionForm: 15 + 1

17) ValueExcludeForm: Form to select some items to exclude from the processing

18) EnableURLForm: Form to process the enable field for an action.
"""

import re
from typing import List

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ontask import is_correct_email
from ontask.action.forms import SUFFIX_LENGTH
from ontask.core import forms as ontask_forms
from ontask.dataops.sql.column_queries import is_column_unique
from ontask.dataops.sql.row_queries import get_rows
from ontask.models import Action, Column

# Format of column name to produce a Moodle compatible ZIP
participant_re = re.compile(r'^Participant \d+$')

SUBJECT_FIELD_LENGTH = 512


class ExportWorkflowBase(ontask_forms.FormWithPayload):
    """Class to include a boolean flag to export a workflow."""

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.'),
    )

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.set_field_from_dict('export_wf')

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        self.store_fields_in_dict([('export_wf', None)])

        return form_data


class EmailSubjectFormBase(ontask_forms.FormWithPayload):
    """Subject field."""

    subject = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('Email subject'),
    )

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.set_field_from_dict('subject')

    def clean(self):
        """Verify email values."""
        form_data = super().clean()
        self.store_field_in_dict('subject', None)
        return form_data


class EmailCCBCCFormBase(ontask_forms.FormWithPayload):
    """CC and BCC fields."""

    cc_email = forms.CharField(
        label=_('Space-separated list of CC emails'),
        required=False,
    )
    bcc_email = forms.CharField(
        label=_('Space-separated list of BCC emails'),
        required=False,
    )

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.set_fields_from_dict(['subject', 'cc_email', 'bcc_email'])

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        self.store_fields_in_dict([
            ('subject', None),
            (
                'cc_email',
                ' '.join([
                    email.strip()
                    for email in form_data['cc_email'].split() if email
                ])
            ),
            (
                'bcc_email',
                ' '.join([
                    email.strip()
                    for email in form_data['bcc_email'].split() if email
                ])
            )])

        all_correct = all(
            is_correct_email(email) for email in form_data['cc_email'].split())
        if not all_correct:
            self.add_error(
                'cc_email',
                _('Field needs a space-separated list of emails.'),
            )

        all_correct = all(
            is_correct_email(email)
            for email in form_data['bcc_email'].split()
        )
        if not all_correct:
            self.add_error(
                'bcc_email',
                _('Field needs a space-separated list of emails.'),
            )

        return form_data


class ItemColumnConfirmFormBase(ontask_forms.FormWithPayload):
    """Basic form fields to select column for items and confirm boolean."""

    item_column = forms.ModelChoiceField(
        queryset=Column.objects.none(),
        required=True)

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude items before sending?'),
    )

    def __init__(self, *args, **kargs):
        """Store column names and adjust initial values."""
        self.columns: List[str] = kargs.pop('columns')
        super().__init__(*args, **kargs)

        self.set_fields_from_dict(['item_column', 'confirm_items'])

        item_column_pk = self.fields['item_column'].initial
        if item_column_pk is None:
            # Try to guess if there is an "email" column
            item_column_pk = next(
                (col.pk for col in self.columns
                 if col.name.lower() == 'email'),
                None,
            )

        self.fields['item_column'].initial = item_column_pk
        self.fields['item_column'].queryset = self.columns

    def clean(self):
        """Detect uniques values in item_column."""
        form_data = super().clean()

        pcolumn = form_data['item_column']
        self.store_field_in_dict(
            'item_column',
            pcolumn.pk if pcolumn else None)
        self.store_fields_in_dict([('confirm_items', None)])

        # The given column must have unique values
        if not is_column_unique(
            self.action.workflow.get_data_frame_table_name(),
            pcolumn.name,
        ):
            self.add_error(
                'item_column',
                _('Column needs to have all unique values (no empty cells)'),
            )

        return form_data


class JSONTokenForm(ontask_forms.FormWithPayload):
    """Form to include a token field."""

    # Token to use when sending the JSON request
    token = forms.CharField(
        initial='',
        label=_('Authentication Token'),
        strip=True,
        required=True,
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 80,}))

    def __init__(self, *args, **kargs):
        """Modify the fields with the adequate information."""
        super().__init__(*args, **kargs)

        self.set_field_from_dict('token')
        self.fields['token'].help_text = _(
            'Authentication token provided by the external platform.',
        )

    def clean(self):
        """Verify form values."""
        form_data = super().clean()
        self.store_field_in_dict('token')
        return form_data


class EmailActionForm(
    ItemColumnConfirmFormBase,
    EmailSubjectFormBase,
    EmailCCBCCFormBase):
    """Form to edit the Send Email action."""

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Send you a summary message?'),
    )

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Track email reading in an extra column?'),
    )

    def __init__(self, *args, **kargs):
        """Store column names and adjust initial values."""
        super().__init__(*args, **kargs)

        self.fields['item_column'].label = _(
            'Column to use for target email address'),

        self.set_fields_from_dict([
            'send_confirmation',
            'track_read'])

        self.order_fields([
            'item_column',
            'subject',
            'cc_email',
            'bcc_email',
            'confirm_items',
            'send_confirmation',
            'track_read',
            'export_wf'])

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.store_fields_in_dict([
            ('send_confirmation', None),
            ('track_read', None)])

        # Check if the values in the item_column are correct emails
        pcolumn = form_data['item_column']
        try:
            column_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[pcolumn.name])
            if not all(is_correct_email(iname[0]) for iname in column_data):
                # column has incorrect email addresses
                self.add_error(
                    'item_column',
                    _('The column with email addresses has incorrect values.'),
                )
        except TypeError:
            self.add_error(
                'item_column',
                _('The column with email addresses has incorrect values.'),
            )

        return form_data

    class Meta(object):
        """Redefine size of the subject field."""

        widgets = {'subject': forms.TextInput(
            attrs={'size': SUBJECT_FIELD_LENGTH})}


class EmailActionRunForm(EmailActionForm, ExportWorkflowBase):
    """Form to edit the Send Email Action Run."""

    def __init__(self, *args, **kargs):
        """Adjust initial values."""
        super().__init__(*args, **kargs)

        self.fields['item_column'].label = _(
            'Column to use for target email address'),

        self.order_fields([
            'item_column',
            'subject',
            'cc_email',
            'bcc_email',
            'confirm_items',
            'send_confirmation',
            'track_read',
            'export_wf'])


class SendListActionForm(EmailSubjectFormBase, EmailCCBCCFormBase):
    """Form to edit the Send Email action."""

    email_to = forms.CharField(label=_('Recipient'), required=True)

    def __init__(self, *args, **kargs):
        """Sort the fields."""
        super().__init__(*args, **kargs)

        self.set_field_from_dict('email_to')


    def clean(self):
        """Verify recipient email value"""
        form_data = super().clean()

        self.store_field_in_dict('email_to')
        if not is_correct_email(form_data['email_to']):
            self.add_error(
                'email_to',
                _('Field needs a valid email address.'),
            )

        return form_data


class SendListActionRunForm(SendListActionForm, ExportWorkflowBase):
    """Form to edit the Send Email action Run."""

    def __init__(self, *args, **kargs):
        """Sort the fields."""
        super().__init__(*args, **kargs)
        self.order_fields([
            'email_to',
            'subject',
            'cc_email',
            'bcc_email',
            'export_wf'])


class ZipActionRunForm(ItemColumnConfirmFormBase, ExportWorkflowBase):
    """Form to create a ZIP."""

    user_fname_column = forms.ChoiceField(
        label=_(
            'Column to use for file name prefix (Full name if Moodle ZIP)',
        ),
        required=False,
    )

    file_suffix = forms.CharField(
        max_length=SUFFIX_LENGTH,
        strip=True,
        required=False,
        label='File name suffix ("feedback.html" if empty)',
    )

    zip_for_moodle = forms.BooleanField(
        initial=False,
        required=False,
        label=_('This ZIP will be uploaded to Moodle as feedback'),
    )

    def __init__(self, *args, **kargs):
        """Store column names, action and payload, adjust fields."""
        super().__init__(*args, **kargs)

        self.fields['item_column'].label = _(
            'Key column to use for file name prefix (Participant id if '
            + 'Moodle ZIP)')

        self.set_fields_from_dict([
            'user_fname_column',
            'file_suffix',
            'zip_for_moodle'])

        # Get the initial values for certain fields
        user_fname_column = self.fields['user_fname_column'].initial

        ufn_field = self.fields['user_fname_column']
        if user_fname_column:
            ufn_field.choices = [
                (col.name, col.name) for col in self.columns]
            ufn_field.initial = user_fname_column
        else:
            ufn_field.choices = [('', '---')] + [
                (col.name, col.name) for col in self.columns
            ]
            ufn_field.initial = ('', '---')

        self.order_fields([
            'item_column',
            'confirm_items',
            'user_fname_columns',
            'file_suffix',
            'zip_for_moodle',
            'export_wf'])

    def clean(self):
        """Detect uniques values in one column, and different column names."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.store_fields_in_dict([
            ('user_fname_column', None),
            ('file_suffix', None),
            ('zip_for_moodle', None)])

        # Participant column must be unique
        pcolumn = form_data['item_column']
        ufname_column = form_data['user_fname_column']

        # If both values are given and they are identical, return with error
        if pcolumn and ufname_column and pcolumn == ufname_column:
            self.add_error(
                None,
                _('The two columns must be different'),
            )
            return form_data

        # If a moodle zip has been requested
        if form_data.get('zip_for_moodle'):
            if not pcolumn or not ufname_column:
                self.add_error(
                    None,
                    _('A Moodle ZIP requires two column names'),
                )
                return form_data

            # Participant columns must match the pattern 'Participant [0-9]+'
            pcolumn_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[pcolumn])
            participant_error = any(
                not participant_re.search(str(row[pcolumn]))
                for row in pcolumn_data
            )
            if participant_error:
                self.add_error(
                    'item_column',
                    _('Values in column must have format '
                      + '"Participant [number]"'),
                )

        return form_data


class CanvasEmailActionForm(ItemColumnConfirmFormBase, EmailSubjectFormBase):
    """Form to process information to run a Canvas Email action."""

    def __init__(self, *args, **kargs):
        """Modify certain field data."""
        super().__init__(*args, **kargs)

        if len(settings.CANVAS_INFO_DICT) > 1:
            # Add the target_url field if the system has more than one entry
            # point configured
            self.fields['target_url'] = forms.ChoiceField(
                initial=self._FormWithPayload__form_info.get(
                    'target_url', None),
                required=True,
                choices=[('', '---')] + [(key, key) for key in sorted(
                    settings.CANVAS_INFO_DICT.keys(),
                )],
                label=_('Canvas Host'),
                help_text=_('Name of the Canvas host to send the messages'),
            )
            self.set_field_from_dict('target_url')

        # Rename field labels
        self.fields['item_column'].label = _('Column with the Canvas ID')
        self.fields['confirm_items'].label = _(
            'Check/Exclude Canvas IDs before sending?',
        )

        self.order_fields([
            'item_column',
            'subject',
            'target_url',
            'confirm_items',
            'export_wf'],
        )

    def clean(self):
        """Store the target_url if not part of the form"""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.store_field_in_dict('target_url', None)

        target_url = self._FormWithPayload__form_info.get('target_url', None)
        if not target_url:
            self.store_field_in_dict(
                'target_url',
                next(iter(settings.CANVAS_INFO_DICT.keys())))
        if not self.get_payload_field('target_url'):
            self.add_error(
                None,
                _('No Canvas Service available for this action.'),
            )

        return form_data

    class Meta(object):
        """Set the size for the subject field."""

        widgets = {'subject': forms.TextInput(
            attrs={'size': SUBJECT_FIELD_LENGTH})}


class CanvasEmailActionRunForm(CanvasEmailActionForm, ExportWorkflowBase):
    """Form to process information to run a Canvas Email action."""

    def __init__(self, *args, **kargs):
        """Modify certain field data."""
        super().__init__(*args, **kargs)

        self.order_fields([
            'item_column',
            'subject',
            'target_url',
            'confirm_items',
            'export_wf'],
        )


class JSONActionForm(ItemColumnConfirmFormBase, JSONTokenForm):
    """Form to edit information to run a JSON action."""

    def __init__(self, *args, **kargs):
        """Modify the fields with the adequate information."""
        super().__init__(*args, **kargs)

        self.fields['item_column'].label = _(
            'Column to exclude objects to send (empty to skip step)',
        )


class JSONActionRunForm(JSONActionForm, ExportWorkflowBase,
):
    """Form to edit information to run a JSON action Run"""

    def __init__(self, *args, **kargs):
        """Modify the fields with the adequate information."""
        super().__init__(*args, **kargs)

        self.order_fields([
            'item_column',
            'token',
            'confirm_items',
            'export_wf'])


class JSONListActionForm(JSONTokenForm):
    """Use a synonym for consistency with the other classes"""
    pass


class JSONListActionRunForm(JSONListActionForm, ExportWorkflowBase):
    """Form to edit information to run JSON List action"""
    def __init__(self, *args, **kargs):
        """Modify the fields with the adequate information."""
        super().__init__(*args, **kargs)

        self.order_fields([
            'token',
            'export_wf'])


class ValueExcludeForm(ontask_forms.FormWithPayload):
    """Form to select a few fields to exclude."""

    # Values to exclude
    exclude_values = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label=_('Values to exclude'),
    )

    def __init__(self, form_data, *args, **kwargs):
        """Store action, column name and exclude init, adjust fields."""
        self.column_name: str = kwargs.pop('column_name', None)
        self.exclude_init: List[str] = kwargs.pop('exclude_values', list)

        super().__init__(form_data, *args, **kwargs)

        self.fields['exclude_values'].choices = get_rows(
            self.action.workflow.get_data_frame_table_name(),
            column_names=[self.column_name, self.column_name],
            filter_formula=self.action.get_filter_formula()).fetchall()
        self.set_field_from_dict('exclude_values')

    def clean(self):
        """Store the values in the field in the dictionary."""
        form_data = super().clean()
        self.store_field_in_dict('exclude_values')
        return form_data


class EnableURLForm(forms.ModelForm):
    """Form to edit the serve_enabled, active_from, and active_to."""

    def clean(self):
        """Verify given datetimes."""
        form_data = super().clean()

        # Check the datetimes. One needs to be after the other
        a_from = self.cleaned_data.get('active_from')
        a_to = self.cleaned_data.get('active_to')
        if a_from and a_to and a_from >= a_to:
            self.add_error(
                'active_from',
                _('Incorrect date/time window'),
            )
            self.add_error(
                'active_to',
                _('Incorrect date/time window'),
            )

        return form_data

    class Meta(object):
        """Define fields and datetime picker widget."""

        model = Action
        fields = ('serve_enabled', 'active_from', 'active_to')

        widgets = {
            'active_from': DateTimePickerInput(
                options=ontask_forms.date_time_widget_options),
            'active_to': DateTimePickerInput(
                options=ontask_forms.date_time_widget_options)}
