"""Forms to manage the connections."""
from typing import Dict

from django import forms
from django.core import signing
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core import forms as ontask_forms
from ontask.dataops import forms as dataops_forms


class ConnectionForm(forms.ModelForm):
    """Base class for connection forms."""
    pass


class SQLConnectionForm(ConnectionForm):
    """Form to read data from SQL.

    We collect information to create a Database URI to be used by SQLAlchemy:

    dialect[+driver]://user:password@host/dbname[?key=value..]
    """

    def clean(self) -> Dict:
        """Validate the initial value."""
        form_data = super().clean()

        # Check if the name already exists
        name_exists = models.SQLConnection.objects.filter(
            name=self.cleaned_data['name'],
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already a connection with this name.'),
            )

        return form_data

    class Meta(ConnectionForm):
        """Define the model and the fields to manipulate."""

        model = models.SQLConnection

        fields = [
            'name',
            'description_text',
            'conn_type',
            'conn_driver',
            'db_user',
            'db_password',
            'db_host',
            'db_port',
            'db_name',
            'db_table',
        ]


class SQLRequestConnectionParam(ontask_forms.FormWithPayload):
    """Form to ask for a password for a SQL connection execution."""

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection')
        super().__init__(*args, **kwargs)

        if not self.connection.db_password:
            self.fields['db_password'] = forms.CharField(
                max_length=models.CHAR_FIELD_MID_SIZE,
                label=_('Password'),
                widget=forms.PasswordInput,
                required=True,
                help_text=_('Authentication for the database connection'))

        if not self.connection.db_table:
            self.fields['db_table'] = forms.CharField(
                max_length=models.CHAR_FIELD_MID_SIZE,
                label=_('Table name'),
                required=True,
                help_text=_('Table to load'))
            self.set_fields_from_dict(['db_table'])

    def clean(self) -> Dict:
        """Store the fields in the Form Payload"""
        form_data = super().clean()

        if 'db_password' in self.fields:
            self.store_fields_in_dict([
                ('db_password', signing.dumps(form_data['db_password']))])

        if 'db_table' in self.fields:
            self.store_fields_in_dict([('db_table', None)])

        return form_data


class AthenaConnectionForm(ConnectionForm):
    """Form to read data from SQL.

    We collect information to open a connection to an Athena instance
    """

    def clean(self) -> Dict:
        """Validate the initial value."""
        form_data = super().clean()

        # Check if the name already exists
        name_exists = models.AthenaConnection.objects.filter(
            name=self.cleaned_data['name'],
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already a connection with this name.'),
            )

        return form_data

    class Meta(ConnectionForm):
        """Define the model and the fields to manipulate."""

        model = models.AthenaConnection

        fields = [
            'name',
            'description_text',
            'aws_access_key',
            'aws_secret_access_key',
            'aws_session_token',
            'aws_bucket_name',
            'aws_file_path',
            'aws_region_name',
            'table_name']


class AthenaRequestConnectionParam(forms.Form):
    """Form to ask for a password for a SQL connection execution."""

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.workflow = kwargs.pop('workflow')

        super().__init__(*args, **kwargs)

        if not self.instance.aws_secret_access_key:
            self.fields['aws_secret_access_key'] = forms.CharField(
                max_length=models.CHAR_FIELD_LONG_SIZE,
                required=True,
                help_text=_('Authentication for the connection'))

        if not self.instance.aws_session_token:
            self.fields['aws_session_token'] = forms.CharField(
                max_length=models.CHAR_FIELD_LONG_SIZE,
                required=False,
                widget=forms.Textarea,
                help_text=_('Authentication for the session'))

        if not self.instance.table_name:
            self.fields['table_name'] = forms.CharField(
                max_length=models.CHAR_FIELD_MID_SIZE,
                required=True,
                help_text=_('Table to load'))

        if self.workflow.has_data_frame:
            if self.workflow.columns.filter(is_key=True).count() > 1:
                merge_choices = [
                    (skey, skey)
                    for skey in self.workflow.columns.filter(is_key=True)
                ]
                # Insert field to choose unique key
                self.fields['merge_key'] = forms.ChoiceField(
                    initial=None,
                    choices=merge_choices,
                    required=True,
                    label=_('Key Column in Existing Table'),
                    help_text=dataops_forms.SelectKeysForm.dst_help)

            self.fields['how_merge'] = forms.ChoiceField(
                initial=None,
                choices=dataops_forms.MergeForm.how_merge_choices,
                required=True,
                label=_('Method to select rows to merge'),
                help_text=dataops_forms.MergeForm.merge_help)

    def get_field_dict(self):
        """Return a dictionary with the resulting fields"""
        to_return = self.instance.get_missing_fields(self.cleaned_data)

        if self.workflow.has_data_frame:
            try:
                to_return['merge_key'] = self.workflow.columns.filter(
                    is_key=True).get().name
            except models.Workflow.MultipleObjectsReturned:
                to_return['merge_key'] = self.cleaned_data['merge_key']

            to_return['merge_method'] = self.cleaned_data['how_merge']

        return to_return
