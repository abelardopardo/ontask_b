# -*- coding: utf-8 -*-

"""Forms to upload, import and export a workflow."""
import json
from typing import Dict

from django import forms
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core import RestrictedFileField
from ontask.models.common import CHAR_FIELD_SMALL_SIZE
import ontask.settings


class WorkflowForm(forms.ModelForm):
    """Workflow create form."""

    def __init__(self, *args, **kwargs):
        """Store the user to put as owner of the workflow."""
        self.user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

    def clean(self) -> Dict:
        """Check if the name for the workflow is unique."""
        form_data = super().clean()

        if not self.cleaned_data.get('name'):
            self.add_error(
                'name',
                _('You need to provide a name for the workflow.'),
            )
            return form_data

        # Store the user in the instance
        self.instance.user = self.user

        # Check if the name already exists
        name_exists = models.Workflow.objects.filter(
            user=self.user,
            name=self.cleaned_data['name']
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('A workflow with this name already exists'),
            )

        return form_data

    class Meta:
        """Identify the model and the fields."""

        model = models.Workflow
        fields = ['name', 'description_text']


class WorkflowImportForm(forms.Form):
    """Form to import a workflow (processing name and file)."""

    name = forms.CharField(
        max_length=CHAR_FIELD_SMALL_SIZE,
        strip=True,
        required=False,
        initial='',
        label='Name (leave empty to take the name stored in the file)')

    wf_file = RestrictedFileField(
        max_upload_size=int(ontask.settings.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask.settings.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File'),
        help_text=_('File containing a previously exported workflow'))

    def __init__(self, *args, **kwargs):
        """Store the user that prompted the request."""
        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

    def clean(self) -> Dict:
        """Check that the name is unique and form multipart."""
        form_data = super().clean()

        if not self.is_multipart():
            self.add_error(
                None,
                _('Incorrect form request (it is not multipart)'),
            )

        # Check if the name already exists
        name_exists = models.Workflow.objects.filter(
            user=self.user,
            name=self.cleaned_data['name']).exists()
        if name_exists:
            self.add_error(
                'name',
                _('A workflow with this name already exists'),
            )

        return form_data


class WorkflowExportRequestForm(forms.Form):
    """Form to request which actions to export from the workflow."""

    def __init__(self, *args, **kargs):
        """Set actions, prefix and labels.

        Kargs contain: actions: list of action objects

        :param args:
        :param kargs: Additional arguments such as list  of actions,
        field_prefix
        """
        workflow = kargs.pop('workflow')

        # List of columns to process and a field prefix
        self.actions = workflow.actions.all()
        self.field_prefix = kargs.pop('field_prefix', 'select_')

        super().__init__(*args, **kargs)

        # Create as many fields as the given actions
        for idx, action in enumerate(self.actions):
            self.fields[self.field_prefix + '%s' % idx] = forms.BooleanField(
                label=action.name,
                label_suffix='',
                required=False)
