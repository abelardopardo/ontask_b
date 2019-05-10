# -*- coding: utf-8 -*-

"""Forms to upload, import and export a workflow."""

import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from ontask import ontask_prefs
from ontask.forms import RestrictedFileField
from workflow.models import Workflow

CHAR_FIELD_LENGTH = 512


class WorkflowForm(forms.ModelForm):
    """Worflow create form."""

    def __init__(self, *args, **kwargs):
        """Store the user to put as owner of the workflow."""
        self.user = kwargs.pop('workflow_user', None)
        super().__init__(*args, **kwargs)

    class Meta(object):
        """Identify the model and the fields."""

        model = Workflow

        fields = ['name', 'description_text']


class WorkflowImportForm(forms.Form):
    """Form to import a workflow (processing name and file)."""

    name = forms.CharField(
        max_length=CHAR_FIELD_LENGTH,
        strip=True,
        required=False,
        initial='',
        label='Name (leave empty to take the name stored in the file)')

    wf_file = RestrictedFileField(
        max_upload_size=int(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File'),
        help_text=_('File containing a previously exported workflow'))


class WorkflowExportRequestForm(forms.Form):
    """Form to request which actions to export from the workflow."""

    def __init__(self, *args, **kargs):
        """Set actions, prefix and labels.

        Kargs contain: actions: list of action objects, put_labels: boolean
        stating if the labels should be included in the form

        :param args:

        :param kargs:
        """
        # List of columns to process and a field prefix
        self.actions = kargs.pop('actions', [])
        self.field_prefix = kargs.pop('field_prefix', 'select_')

        # Should the labels be included?
        self.put_labels = kargs.pop('put_labels')

        super().__init__(*args, **kargs)

        # Create as many fields as the given columns
        for idx, action in enumerate(self.actions):
            # Include the labels if requested
            if self.put_labels:
                label = action.name
            else:
                label = ''

            self.fields[self.field_prefix + '%s' % idx] = forms.BooleanField(
                label=label,
                label_suffix='',
                required=False)
