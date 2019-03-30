# -*- coding: utf-8 -*-


import json
import re
from builtins import next
from builtins import object
from builtins import str

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.conf import settings as ontask_settings
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteInplaceWidget

from dataops.pandas_db import (
    execute_select_on_table, get_table_cursor,
    is_column_table_unique, get_table_data
)
from ontask import ontask_prefs, is_legal_name, is_correct_email
from ontask.forms import (
    column_to_field, RestrictedFileField,
    dateTimeWidgetOptions
)
from .models import Action, Condition

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___select_'

participant_re = re.compile(r'^Participant \d+$')


class ActionUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(str('workflow_user'), None)
        self.workflow = kwargs.pop(str('action_workflow'), None)
        super(ActionUpdateForm, self).__init__(*args, **kwargs)

    class Meta(object):
        model = Action
        fields = ('name', 'description_text')


class ActionForm(ActionUpdateForm):
    def __init__(self, *args, **kargs):
        super(ActionForm, self).__init__(*args, **kargs)

        self.fields['action_type'].widget.choices = \
            Action.AVAILABLE_ACTION_TYPES
        # Remove those actions that are not available
        if len(Action.AVAILABLE_ACTION_TYPES) == 1:
            # There is only one type of action. No need to generate the field.
            # Set to value and hide
            self.fields['action_type'].widget = forms.HiddenInput()
            self.fields['action_type'].initial = \
                Action.AVAILABLE_ACTION_TYPES[0][0]

    class Meta(object):
        model = Action
        fields = ('name', 'description_text', 'action_type')


class ActionDescriptionForm(forms.ModelForm):
    class Meta(object):
        model = Action
        fields = ('description_text',)


class EditActionOutForm(forms.ModelForm):
    """
    Main class to edit an action out.
    """
    content = forms.CharField(label='', required=False)

    def __init__(self, *args, **kargs):

        super(EditActionOutForm, self).__init__(*args, **kargs)

        # Personalized text, canvas email
        if self.instance.action_type == Action.PERSONALIZED_TEXT:
            self.fields['content'].widget = SummernoteInplaceWidget()

        # Add the Target URL field
        if self.instance.action_type == Action.PERSONALIZED_JSON:
            # Add the target_url field
            self.fields['target_url'] = forms.CharField(
                initial=self.instance.target_url,
                label=_('Target URL'),
                strip=True,
                required=False,
                widget=forms.Textarea(
                    attrs={
                        'rows': 1,
                        'cols': 80,
                        'placeholder': _('URL to send the personalized JSON')
                    }
                )
            )

        if self.instance.action_type == Action.PERSONALIZED_JSON:
            # Modify the content field so that it uses the TextArea
            self.fields['content'].widget = forms.Textarea(
                attrs={'cols': 80,
                       'rows': 15,
                       'placeholder': _('Write a JSON object')}
            )

        if self.instance.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
            # Modify the content field so that it uses the TextArea
            self.fields['content'].widget = forms.Textarea(
                attrs={'cols': 80,
                       'rows': 15,
                       'placeholder': _('Write a plain text message')}
            )

    class Meta(object):
        model = Action
        fields = ('content',)


# Form to enter values in a row
class EnterActionIn(forms.Form):

    def __init__(self, *args, **kargs):

        # Store the instance
        self.columns = kargs.pop('columns', None)
        self.values = kargs.pop('values', None)
        self.show_key = kargs.pop('show_key', False)

        super(EnterActionIn, self).__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.values:
            self.values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):

            # Skip the key columns if flag is true
            if not self.show_key and column.is_key:
                continue

            self.fields[field_prefix + '%s' % idx] = \
                column_to_field(column,
                                self.values[idx],
                                label=column.description_text)

            if column.is_key:
                self.fields[field_prefix + '%s' % idx].widget.attrs[
                    'readonly'
                ] = 'readonly'
                self.fields[field_prefix + '%s' % idx].disabled = True


class FilterForm(forms.ModelForm):
    """
    Form to read information about a filter. The required property of the
    formula field is set to False because it is enforced in the server.
    """

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

    class Meta(object):
        model = Condition
        fields = ('description_text', 'formula')


class ConditionForm(forms.ModelForm):
    """
    Form to read information about a condition. The same as the filter but we
    need to enforce that the name is a valid variable name
    """

    def __init__(self, *args, **kwargs):

        super(ConditionForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

        # Remember the condition name to perform content substitution
        self.old_name = None,
        if hasattr(self, 'instance'):
            self.old_name = self.instance.name

    def clean(self):
        data = super(ConditionForm, self).clean()

        if not data.get('name'):
            self.add_error('name', _('Name cannot be empty'))
            return data

        msg = is_legal_name(data['name'])
        if msg:
            self.add_error('name', msg)
            return data

        return data

    class Meta(object):
        model = Condition
        fields = ('name', 'description_text', 'formula')


class EnableURLForm(forms.ModelForm):

    def clean(self):
        data = super(EnableURLForm, self).clean()

        # Check the datetimes. One needs to be after the other
        a_from = self.cleaned_data['active_from']
        a_to = self.cleaned_data['active_to']
        if a_from and a_to and a_from >= a_to:
            self.add_error(
                'active_from',
                _('Incorrect date/time window')
            )
            self.add_error(
                'active_to',
                _('Incorrect date/time window')
            )

        return data

    class Meta(object):
        model = Action
        fields = ('serve_enabled', 'active_from', 'active_to')

        widgets = {
            'active_from': DateTimePickerInput(options=dateTimeWidgetOptions),
            'active_to': DateTimePickerInput(options=dateTimeWidgetOptions),
        }


class EmailActionForm(forms.Form):
    subject = forms.CharField(max_length=1024,
                              strip=True,
                              required=True,
                              label=_('Email subject'))

    email_column = forms.ChoiceField(
        label=_('Column to use for target email address'),
        required=True
    )

    cc_email = forms.CharField(
        label=_('Comma separated list of CC emails'),
        required=False
    )
    bcc_email = forms.CharField(
        label=_('Comma separated list of BCC emails'),
        required=False
    )

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude email addresses before sending?')
    )

    send_confirmation = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Send you a summary message?')
    )

    track_read = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Track email reading in an extra column?')
    )

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.')
    )

    def __init__(self, *args, **kargs):
        self.column_names = kargs.pop('column_names')
        self.action = kargs.pop('action')
        self.op_payload = kargs.pop('op_payload')

        super(EmailActionForm, self).__init__(*args, **kargs)

        # Set the initial values from the payload
        self.fields['subject'].initial = self.op_payload.get('subject', '')
        email_column = self.op_payload.get('item_column', None)
        self.fields['cc_email'].initial = self.op_payload.get('cc_email', '')
        self.fields['bcc_email'].initial = self.op_payload.get('bcc_email', '')
        self.fields['confirm_items'].initial = self.op_payload.get(
            'confirm_items',
            False
        )
        self.fields['send_confirmation'].initial = self.op_payload.get(
            'send_confirmation',
            False
        )
        self.fields['track_read'].initial = self.op_payload.get('track_read',
                                                                False)
        self.fields['export_wf'].initial = self.op_payload.get('export_wf',
                                                               False)

        if email_column is None:
            # Try to guess if there is an "email" column
            email_column = next((x for x in self.column_names
                                 if 'email' == x.lower()), None)

        if email_column is None:
            email_column = ('', '---')
        else:
            email_column = (email_column, email_column)
        self.fields['email_column'].initial = email_column
        self.fields['email_column'].choices = \
            [(x, x) for x in self.column_names]

    def clean(self):
        data = super(EmailActionForm, self).clean()

        email_column = self.cleaned_data['email_column']

        # Check if the values in the email column are correct emails
        try:
            column_data = execute_select_on_table(
                self.action.workflow.get_data_frame_table_name(),
                [],
                [],
                column_names=[email_column]
            )
            if not all([is_correct_email(x[0]) for x in column_data]):
                # column has incorrect email addresses
                self.add_error(
                    'email_column',
                    _('The column with email addresses has incorrect values.')
                )
        except TypeError:
            self.add_error(
                'email_column',
                _('The column with email addresses has incorrect values.')
            )

        if not all([is_correct_email(x.strip())
                    for x in self.cleaned_data['cc_email'].split(',') if x]):
            self.add_error(
                'cc_email',
                _('Field needs a comma-separated list of emails.')
            )

        if not all([is_correct_email(x)
                    for x in self.cleaned_data['bcc_email'].split(',') if x]):
            self.add_error(
                'bcc_email',
                _('Field needs a comma-separated list of emails.')
            )

        return data

    class Meta(object):
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class ZipActionForm(forms.Form):
    participant_column = forms.ChoiceField(
        label=_('Key column to use for file name prefix (Participant id if '
                'Moodle ZIP)'),
        required=True
    )

    user_fname_column = forms.ChoiceField(
        label=_('Column to use for file name prefix (Full name if Moodle ZIP)'),
        required=False
    )

    file_suffix = forms.CharField(
        max_length=512,
        strip=True,
        required=False,
        label='File name suffix ("feedback.html" if empty)'
    )

    zip_for_moodle = forms.BooleanField(
        initial=False,
        required=False,
        label=_('This ZIP will be uploaded to Moodle as feedback')
    )

    confirm_users = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude users before sending?')
    )

    def __init__(self, *args, **kargs):
        self.column_names = kargs.pop('column_names')
        self.action = kargs.pop('action')
        self.op_payload = kargs.pop('op_payload')

        super(ZipActionForm, self).__init__(*args, **kargs)

        # Set the initial values from the payload
        user_fname_column = self.op_payload.get('user_fname_column', None)
        participant_column = self.op_payload.get('item_column', None)

        if user_fname_column:
            self.fields['user_fname_column'].choices = \
                [(x, x) for x in self.column_names]
            self.fields['user_fname_column'].initial = user_fname_column
        else:
            self.fields['user_fname_column'].choices = \
                [('', '---')] + [(x, x) for x in self.column_names]
            self.fields['user_fname_column'].initial = ('', '---')

        if participant_column:
            self.fields['participant_column'].choices = \
                [(x, x) for x in self.column_names]
            self.fields['participant_column'].initial = participant_column
        else:
            self.fields['participant_column'].choices = \
                [('', '---')] + [(x, x) for x in self.column_names]
            self.fields['participant_column'].initial = ('', '---')

        self.fields['confirm_users'].initial = self.op_payload.get(
            'confirm_users', False)

    def clean(self):
        data = super(ZipActionForm, self).clean()

        # Participant column must be unique
        pcolumn = data['participant_column']
        ufname_column = data['user_fname_column']

        # The given column must have unique values
        if not is_column_table_unique(
                self.action.workflow.get_data_frame_table_name(),
                pcolumn
        ):
            self.add_error(
                'participant_column',
                _('Column needs to have all unique values (no empty cells)')
            )
            return data

        # If both values are given and they are identical, return with error
        if pcolumn and ufname_column and pcolumn == ufname_column:
            self.add_error(
                None,
                _('The two columns must be different')
            )
            return data

        # If a moodle zip has been requested
        if data.get('zip_for_moodle', False):
            if not pcolumn or not ufname_column:
                self.add_error(
                    None,
                    _('A Moodle ZIP requires two column names')
                )
                return data

            # Participant columns must match the pattern 'Participant [0-9]+'
            pcolumn_data = get_table_data(
                self.action.workflow.get_data_frame_table_name(),
                None,
                column_names=[pcolumn]
            )
            if next((x for x in pcolumn_data
                     if not participant_re.search(str(x[0]))),
                    None):
                self.add_error(
                    'participant_column',
                    _('Values in column must have format '
                      '"Participant [number]"')
                )

        return data


class EmailExcludeForm(forms.Form):
    # Email fields to exclude
    exclude_values = forms.MultipleChoiceField(choices=[],
                                               required=False,
                                               label=_('Values to exclude'))

    def __init__(self, data, *args, **kwargs):
        self.action = kwargs.pop('action', None)
        self.column_name = kwargs.pop('column_name', None)
        self.exclude_init = kwargs.pop('exclude_values', list)

        super(EmailExcludeForm, self).__init__(data, *args, **kwargs)

        self.fields['exclude_values'].choices = \
            get_table_cursor(self.action.workflow.get_data_frame_table_name(),
                             self.action.get_filter(),
                             [self.column_name, self.column_name]).fetchall()
        self.fields['exclude_values'].initial = self.exclude_init


class JSONBasicActionForm(forms.Form):
    # Column with unique key to select objects/send email
    key_column = forms.ChoiceField(required=True)

    confirm_items = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Check/exclude items before sending?')
    )

    def __init__(self, *args, **kargs):

        self.column_names = kargs.pop('column_names')
        self.op_payload = kargs.pop('op_payload')

        super(JSONBasicActionForm, self).__init__(*args, **kargs)

        # Handle the key column setting the initial value if given and
        # selecting the choices
        key_column = self.op_payload.get('item_column', None)
        if key_column is None:
            key_column = ('', '---')
        else:
            key_column = (key_column, key_column)
        self.fields['key_column'].initial = key_column
        self.fields['key_column'].choices = [('', '---')] + \
                                            [(x, x) for x in self.column_names]

        self.fields['confirm_items'].initial = self.op_payload.get(
            'confirm_items',
            False
        )


class JSONActionForm(JSONBasicActionForm):
    # Token to use when sending the JSON request
    token = forms.CharField(
        initial='',
        label=_('Authentication Token'),
        strip=True,
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'cols': 120,
                # 'placeholder':
                #     _('Authentication token to communicate with the platform')
            }
        )
    )

    def __init__(self, *args, **kargs):
        super(JSONActionForm, self).__init__(*args, **kargs)

        self.fields['key_column'].label = \
            _('Column to exclude objects to send (empty to skip step)')
        self.fields['key_column'].required = False

        self.fields.pop('confirm_items')

        self.fields['token'].initial = self.op_payload.get('token', '')
        self.fields['token'].help_text = \
            _('Authentication token provided by the external platform.')

        self.order_fields(['key_column', 'token'])


class CanvasEmailActionForm(JSONBasicActionForm):
    subject = forms.CharField(max_length=1024,
                              strip=True,
                              required=True,
                              label=_('Email subject'))

    export_wf = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Download a snapshot of the workflow?'),
        help_text=_('A zip file is useful to review the emails sent.')
    )

    def __init__(self, *args, **kargs):
        self.action = kargs.pop('action')

        super(CanvasEmailActionForm, self).__init__(*args, **kargs)

        if len(ontask_settings.CANVAS_INFO_DICT) > 1:
            # Add the target_url field if the system has more than one entry
            # point configured
            self.fields['target_url'] = forms.ChoiceField(
                initial=self.action.target_url,
                required=True,
                choices=[('', '---')] + [(x, x) for x in sorted(
                    ontask_settings.CANVAS_INFO_DICT.keys()
                )],
                label=_('Canvas Host'),
                help_text=_('Name of the Canvas host to send the messages')
            )

        self.fields['key_column'].label = _('Column with the Canvas ID')
        self.fields['confirm_items'].label = \
            _('Check/Exclude Canvas IDs before sending?')
        self.fields['subject'].initial = self.op_payload.get('subject', '')
        self.fields['confirm_items'].initial = self.op_payload.get(
            'confirm_items',
            False
        )
        self.fields['export_wf'].initial = self.op_payload.get('export_wf',
                                                               False)
        self.order_fields(['key_column',
                           'subject',
                           'target_url',
                           'confirm_items',
                           'export_wf'])

    class Meta(JSONBasicActionForm):
        widgets = {'subject': forms.TextInput(attrs={'size': 256})}


class ActionImportForm(forms.Form):
    # Action name
    name = forms.CharField(
        max_length=512,
        strip=True,
        required=True,
        label='Name')

    file = RestrictedFileField(
        max_upload_size=int(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File'),
        help_text=_('File containing a previously exported action'))
