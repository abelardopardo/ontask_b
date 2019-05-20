# -*- coding: utf-8 -*-

"""Forms to process action execution.

EmailActionForm: Form to process information to send email

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
from typing import Dict, List

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings as ontask_settings
from django.utils.translation import ugettext_lazy as _

from action.forms import SUFFIX_LENGTH
from action.models import Action
from action.payloads import EmailPayload
from dataops.sql.column_queries import is_column_table_unique
from dataops.sql.row_queries import get_rows
from ontask import is_correct_email
from ontask.forms import date_time_widget_options

# Format of column name to produce a Moodle compatible ZIP
participant_re = re.compile(r'^Participant \d+$')


class EmailActionForm(forms.Form):
    """Form to edit the Send Email action."""

    subject = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('Email subject'),
    )

    email_column = forms.ChoiceField(
        label=_('Column to use for target email address'),
        required=True,
    )

    cc_email = forms.CharField(
        label=_('Comma separated list of CC emails'),
        required=False,
    )
    bcc_email = forms.CharField(
        label=_('Comma separated list of BCC emails'),
        required=False,
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

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.'),
    )

    def __init__(self, *args, **kargs):
        """Store column names, action, payload, and adjust initial values."""
        self.column_names: List[str] = kargs.pop('column_names')
        self.action: Action = kargs.pop('action')
        self.action_info: EmailPayload = kargs.pop('action_info')

        super().__init__(*args, **kargs)

        email_column_name = self.fields['email_column'].initial
        if email_column_name is None:
            # Try to guess if there is an "email" column
            email_column_name = next(
                (cname for cname in self.column_names
                 if cname.lower() == 'email'),
                None,
            )

        if email_column_name is None:
            email_column_name = ('', '---')
        else:
            email_column_name = (email_column_name, email_column_name)

        self.fields['email_column'].initial = email_column_name
        self.fields['email_column'].choices = [
            (cname, cname) for cname in self.column_names]

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.action_info['subject'] = form_data['subject']
        self.action_info['item_column'] = form_data['email_column']
        self.action_info['cc_email'] = [
            email.strip()
            for email in form_data['cc_email'].split(',') if email]
        self.action_info['bcc_email'] = [
            email.strip()
            for email in form_data['bcc_email'].split(',') if email]
        self.action_info['confirm_items'] = form_data['confirm_items']
        self.action_info['send_confirmation'] = form_data[
            'send_confirmation'
        ]
        self.action_info['track_read'] = form_data['track_read']
        self.action_info['export_wf'] = form_data['export_wf']

        # Check if the values in the email column are correct emails
        try:
            column_data = get_rows(
                self.action.workflow.get_data_frame_table_name(),
                column_names=[self.action_info['item_column']])
            if not all(is_correct_email(iname[0]) for iname in column_data):
                # column has incorrect email addresses
                self.add_error(
                    'email_column',
                    _('The column with email addresses has incorrect values.'),
                )
        except TypeError:
            self.add_error(
                'email_column',
                _('The column with email addresses has incorrect values.'),
            )

        all_correct = all(
            is_correct_email(email) for email in self.action_info['cc_email']
        )
        if not all_correct:
            self.add_error(
                'cc_email',
                _('Field needs a comma-separated list of emails.'),
            )

        all_correct = all(
            is_correct_email(email) for email in self.action_info['bcc_email']
        )
        if not all_correct:
            self.add_error(
                'bcc_email',
                _('Field needs a comma-separated list of emails.'),
            )

        return form_data

    class Meta(object):
        """Redefine size of the subject field."""

        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class ZipActionForm(forms.Form):
    """Form to create a ZIP."""

    participant_column = forms.ChoiceField(
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
        self.action_info: Dict = kargs.pop('action_info')

        super().__init__(*args, **kargs)

        # Set the initial values from the payload
        user_fname_column = self.action_info.get('user_fname_column')
        participant_column = self.action_info.get('item_column', default=None)

        ufn_field = self.fields['user_fname_column']
        if user_fname_column:
            ufn_field.choices = [(cname, cname) for cname in self.column_names]
            ufn_field.initial = user_fname_column
        else:
            ufn_field.choices = [('', '---')] + [
                (cname, cname) for cname in self.column_names
            ]
            ufn_field.initial = ('', '---')

        pc_field = self.fields['participant_column']
        if participant_column:
            pc_field.choices = [(cname, cname) for cname in self.column_names]
            pc_field.initial = participant_column
        else:
            pc_field.choices = [('', '---')] + [
                (cname, cname) for cname in self.column_names
            ]
            pc_field.initial = ('', '---')

    def clean(self):
        """Detect uniques values in one column, and different column names."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.action_info['item_column'] = form_data['participant_column']
        self.action_info['user_fname_column'] = form_data['user_fname_column']
        self.action_info['file_suffix'] = form_data['file_suffix']
        self.action_info['zip_for_moodle'] = form_data['zip_for_moodle']
        self.action_info['confirm_items'] = form_data['confirm_items']

        # Participant column must be unique
        pcolumn = form_data['participant_column']
        ufname_column = form_data['user_fname_column']

        # The given column must have unique values
        if not is_column_table_unique(
            self.action.workflow.get_data_frame_table_name(),
            pcolumn,
        ):
            self.add_error(
                'participant_column',
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
                    'participant_column',
                    _('Values in column must have format '
                      + '"Participant [number]"'),
                )

        return form_data


class ValueExcludeForm(forms.Form):
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

        self.fields['exclude_values'].choices = get_rows(
            self.action.workflow.get_data_frame_table_name(),
            column_names=[self.column_name, self.column_name],
            filter_formula=self.action.get_filter_formula()).fetchall()
        self.fields['exclude_values'].initial = self.exclude_init


class JSONBasicActionForm(forms.Form):
    """Form to process Basic JSON information."""

    # Column with unique key to select objects/send email
    key_column = forms.ChoiceField(required=True)

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude items before sending?'),
    )

    def __init__(self, *args, **kargs):
        """Store column names, payload and modify key_column and confirm."""
        self.column_names: List = kargs.pop('column_names')
        self.action_info: Dict = kargs.pop('action_info')

        super().__init__(*args, **kargs)

        # Handle the key column setting the initial value if given and
        # selecting the choices
        key_column = self.action_info.get('item_column')
        if key_column is None:
            key_column = ('', '---')
        else:
            key_column = (key_column, key_column)

        self.fields['key_column'].initial = key_column
        self.fields['key_column'].choices = [
            (cname, cname) for cname in self.column_names]


class JSONActionForm(JSONBasicActionForm):
    """Form to edit information to run a JSON action."""

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

        self.fields['key_column'].label = _(
            'Column to exclude objects to send (empty to skip step)',
        )

        self.fields['token'].help_text = _(
            'Authentication token provided by the external platform.',
        )

        self.order_fields(['key_column', 'token', 'confirm_items'])

    def clean(self):
        """Verify form values."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.action_info['token'] = form_data['token']
        self.action_info['item_column'] = form_data['key_column']

        return form_data


class CanvasEmailActionForm(JSONBasicActionForm):
    """Form to process information to run a Canvas Email action."""

    subject = forms.CharField(
        max_length=1024,
        strip=True,
        required=True,
        label=_('Email subject'),
    )

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.'),
    )

    def __init__(self, *args, **kargs):
        """Store the action and modify certain field data."""
        self.action: Action = kargs.pop('action')

        super().__init__(*args, **kargs)

        if len(ontask_settings.CANVAS_INFO_DICT) > 1:
            # Add the target_url field if the system has more than one entry
            # point configured
            self.fields['target_url'] = forms.ChoiceField(
                initial=self.action.target_url,
                required=True,
                choices=[('', '---')] + [(key, key) for key in sorted(
                    ontask_settings.CANVAS_INFO_DICT.keys(),
                )],
                label=_('Canvas Host'),
                help_text=_('Name of the Canvas host to send the messages'),
            )

        self.fields['key_column'].label = _('Column with the Canvas ID')
        self.fields['confirm_items'].label = _(
            'Check/Exclude Canvas IDs before sending?',
        )

        self.order_fields(
            ['key_column',
             'subject',
             'target_url',
             'confirm_items',
             'export_wf'],
        )

    def clean(self):
        """Verify email values."""
        form_data = super().clean()

        # Move data to the payload so that is ready to be used
        self.action_info['subject'] = form_data['subject']
        self.action_info['item_column'] = form_data['key_column']
        self.action_info['confirm_items'] = form_data['confirm_items']
        self.action_info['export_wf'] = form_data['export_wf']
        if not form_data.get('target_url'):
            self.action_info['target_url'] = next(
                iter(ontask_settings.CANVAS_INFO_DICT.keys()),
            )
        if not self.action_info['target_url']:
            self.add_error(
                None,
                _('No Canvas Service available for this action.'),
            )

        return form_data

    class Meta(JSONBasicActionForm):
        """Set the size for the subject field."""

        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class EnableURLForm(forms.ModelForm):
    """Form to edit the serve_enabled, active_from, and active_to."""

    def clean(self):
        """Verify given datetimes."""
        form_data = super().clean()

        # Check the datetimes. One needs to be after the other
        a_from = self.cleaned_data['active_from']
        a_to = self.cleaned_data['active_to']
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
            'active_from': DateTimePickerInput(options=date_time_widget_options),
            'active_to': DateTimePickerInput(options=date_time_widget_options),
        }
