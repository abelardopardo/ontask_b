# -*- coding: utf-8 -*-

"""Forms to process action execution.

BasicEmailForm: Base form for the rest of email forms

EmailActionForm: Form to process information to send email

SendListActionForm: Form to send a single email with list values.

ZipActionForm: Form to process information to create a zip form

ValueExcludeForm: Form to process IDs to exclude from the email form

JSONBasicActionForm: Basic class to process JSON information

JSONActionForm: Inherits from Basic class to process JSON action information

CanvasEmailActionForm: Inherits from JSONBasicAction to process information to
    run a Canvas Email action

ActionImportForm: Form to process information to import an action

EnableURLForm: Form to process the enable, from and to fields of an action
"""

import re
from typing import List

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ontask import is_correct_email
from ontask.action.forms import SUFFIX_LENGTH
from ontask.core.forms import date_time_widget_options, FormWithPayload
from ontask.dataops.sql.column_queries import is_column_unique
from ontask.dataops.sql.row_queries import get_rows
from ontask.models import Action

# Format of column name to produce a Moodle compatible ZIP
participant_re = re.compile(r'^Participant \d+$')

SUBJECT_FIELD_LENGTH = 512


class BasicEmailForm(FormWithPayload):
    """Basic form fields to run an action."""

    subject = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('Email subject'),
    )

    cc_email = forms.CharField(
        label=_('Space-separated list of CC emails'),
        required=False,
    )
    bcc_email = forms.CharField(
        label=_('Space-separated list of BCC emails'),
        required=False,
    )

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.'),
    )

    def __init__(self, *args, **kargs):
        self.action: Action = kargs.pop('action')

        super().__init__(*args, **kargs)

        self.set_fields_from_dict(
            ['subject', 'cc_email', 'bcc_email', 'export_wf'])

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        self.store_fields_in_dict([
            ('subject', None),
            (
                'cc_email',
                (' ').join([
                    email.strip()
                    for email in form_data['cc_email'].split() if email
                ])
            ),
            (
                'bcc_email',
                (' ').join([
                    email.strip()
                    for email in form_data['bcc_email'].split() if email
                ])
            ),
            ('export_wf', None)])

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

class EmailActionForm(BasicEmailForm):
    """Form to edit the Send Email action."""

    item_column = forms.ChoiceField(
        label=_('Column to use for target email address'),
        required=True,
    )

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude email addresses before sending?'),
    )

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
        self.column_names: List[str] = kargs.pop('column_names')

        super().__init__(*args, **kargs)

        self.set_fields_from_dict([
            'item_column',
            'confirm_items',
            'send_confirmation',
            'track_read'])

        item_column_name = self.fields['item_column'].initial
        if item_column_name is None:
            # Try to guess if there is an "email" column
            item_column_name = next(
                (cname for cname in self.column_names
                 if cname.lower() == 'email'),
                None,
            )

        if item_column_name is None:
            item_column_name = ('', '---')
        else:
            item_column_name = (item_column_name, item_column_name)

        self.fields['item_column'].initial = item_column_name
        self.fields['item_column'].choices = [
            (cname, cname) for cname in self.column_names]

        self.order_fields([
            'subject',
            'item_column',
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
            ('item_column', None),
            ('confirm_items', None),
            ('send_confirmation', None),
            ('track_read', None)])

        # Check if the values in the email column are correct emails
        try:
            column_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[self._FormWithPayload__form_info['item_column']])
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


class SendListActionForm(BasicEmailForm):
    """Form to edit the Send Email action."""

    email_to = forms.CharField(label=_('Recipient'), required=True)

    def __init__(self, *args, **kargs):
        """Sort the fields."""
        super().__init__(*args, **kargs)

        self.set_field_from_dict('email_to')

        self.order_fields([
            'email_to',
            'subject',
            'cc_email',
            'bcc_email',
            'export_wf'])

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


class ZipActionForm(FormWithPayload):
    """Form to create a ZIP."""

    item_column = forms.ChoiceField(
        label=_(
            'Key column to use for file name prefix (Participant id if '
            + 'Moodle ZIP)'),
        required=True,
    )

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

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude users before sending?'),
    )

    def __init__(self, *args, **kargs):
        """Store column names, action and payload, adjust fields."""
        self.column_names: List = kargs.pop('column_names')
        self.action: Action = kargs.pop('action')

        super().__init__(*args, **kargs)

        self.set_fields_from_dict([
            'item_column',
            'user_fname_column',
            'file_suffix',
            'zip_for_moodle',
            'confirm_items'])

        # Get the initial values for certain fields
        user_fname_column = self.fields['user_fname_column'].initial
        item_column = self.fields['item_column'].initial

        ufn_field = self.fields['user_fname_column']
        if user_fname_column:
            ufn_field.choices = [(cname, cname) for cname in self.column_names]
            ufn_field.initial = user_fname_column
        else:
            ufn_field.choices = [('', '---')] + [
                (cname, cname) for cname in self.column_names
            ]
            ufn_field.initial = ('', '---')

        pc_field = self.fields['item_column']
        if item_column:
            pc_field.choices = [(cname, cname) for cname in self.column_names]
            pc_field.initial = item_column
        else:
            pc_field.choices = [('', '---')] + [
                (cname, cname) for cname in self.column_names
            ]
            pc_field.initial = ('', '---')

    def clean(self):
        """Detect uniques values in one column, and different column names."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.store_fields_in_dict([
            ('item_column', None),
            ('user_fname_column', None),
            ('file_suffix', None),
            ('zip_for_moodle', None),
            ('confirm_items', None)])

        # Participant column must be unique
        pcolumn = form_data['item_column']
        ufname_column = form_data['user_fname_column']

        # The given column must have unique values
        if not is_column_unique(
            self.action.workflow.get_data_frame_table_name(),
            pcolumn,
        ):
            self.add_error(
                'item_column',
                _('Column needs to have all unique values (no empty cells)'),
            )
            return form_data

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


class ValueExcludeForm(FormWithPayload):
    """Form to select a few fields to exclude."""

    # Values to exclude
    exclude_values = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label=_('Values to exclude'),
    )

    def __init__(self, form_data, *args, **kwargs):
        """Store action, column name and exclude init, adjust fields."""
        self.action: Action = kwargs.pop('action', None)
        self.column_name: str = kwargs.pop('column_name', None)
        self.exclude_init: List[str] = kwargs.pop('exclude_values', list)

        super().__init__(form_data, *args, **kwargs)

        self.set_field_from_dict('exclude_values')
        self.fields['exclude_values'].choices = get_rows(
            self.action.workflow.get_data_frame_table_name(),
            column_names=[self.column_name, self.column_name],
            filter_formula=self.action.get_filter_formula()).fetchall()

    def clean(self):
        """Store the values in the field in the dictionary."""
        form_data = super().clean()
        self.store_field_in_dict('exclude_values')
        return form_data


class JSONBasicForm(FormWithPayload):
    """Form with a token field to run a JSON action."""

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the action.'),
    )

    def __init__(self, *args, **kargs):
        """Store the action item"""
        super().__init__(*args, **kargs)

        self.set_field_from_dict('export_wf')

    def clean(self):
        """Verify form values."""
        form_data = super().clean()

        self.store_field_in_dict('export_wf')

        return form_data


class JSONTokenForm(FormWithPayload):
    """Form to include a token field."""

    # Token to use when sending the JSON request
    token = forms.CharField(
        initial='',
        label=_('Authentication Token'),
        strip=True,
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'cols': 80,
            },
        ),
    )

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


class JSONKeyForm(FormWithPayload):
    """Form to process Basic JSON information."""

    # Column with unique key to select objects/send email
    item_column = forms.ChoiceField(required=True)

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude items before sending?'),
    )

    def __init__(self, *args, **kargs):
        """Store column names, payload and modify item_column and confirm."""
        self.column_names: List = kargs.pop('column_names')

        super().__init__(*args, **kargs)

        self.set_fields_from_dict(['item_column', 'confirm_items'])

        # Handle the key column setting the initial value if given and
        # selecting the choices
        item_column = self.fields['item_column'].initial
        if item_column is None:
            item_column = ('', '---')
        else:
            item_column = (item_column, item_column)

        self.fields['item_column'].initial = item_column
        self.fields['item_column'].choices = [
            (cname, cname) for cname in self.column_names]

    def clean(self):
        """Verify email values."""
        form_data = super().clean()
        self.store_fields_in_dict([
            ('item_column', None), ('confirm_items', None)])
        return form_data


class CanvasEmailActionForm(JSONKeyForm, JSONBasicForm):
    """Form to process information to run a Canvas Email action."""

    subject = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('Email subject'),
    )

    def __init__(self, *args, **kargs):
        """Store the action and modify certain field data."""
        self.action: Action = kargs.pop('action')

        super().__init__(*args, **kargs)

        self.set_field_from_dict('subject')

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
        self.store_fields_in_dict([
            ('subject', None),
            ('target_url', None)])

        target_url = self._FormWithPayload__form_info.get('target_url', None)
        if not target_url:
            self._FormWithPayload__form_info['target_url'] = next(
                iter(settings.CANVAS_INFO_DICT.keys()))
        if not self._FormWithPayload__form_info['target_url']:
            self.add_error(
                None,
                _('No Canvas Service available for this action.'),
            )

        return form_data

    class Meta(object):
        """Set the size for the subject field."""

        widgets = {'subject': forms.TextInput(
            attrs={'size': SUBJECT_FIELD_LENGTH})}


class JSONActionForm(JSONTokenForm, JSONKeyForm, JSONBasicForm):
    """Form to edit information to run a JSON action."""

    def __init__(self, *args, **kargs):
        """Modify the fields with the adequate information."""
        super().__init__(*args, **kargs)

        self.fields['item_column'].label = _(
            'Column to exclude objects to send (empty to skip step)',
        )

        self.order_fields([
            'item_column',
            'token',
            'confirm_items',
            'export_wf'])


class JSONListActionForm(JSONTokenForm, JSONBasicForm):
    """Form to edit information to run JSON List action"""


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
                options=date_time_widget_options),
            'active_to': DateTimePickerInput(options=date_time_widget_options),
        }
