# -*- coding: utf-8 -*-

"""Forms to process action related fields.

ActionUpdateForm: Basic form to process the name/description of an action

ActionForm: Inherits from Basic to process name, description and type

ActionDescriptionForm: Inherits from basic but process only description (for
    surveys)

FilterForm: Form to process filter elements

ConditionForm: Form to process condition elements
"""

import contextlib
import json
from builtins import object, str

from django import forms
from django.utils.translation import ugettext_lazy as _

from action.models import ACTION_NAME_LENGTH, Action, Condition
from ontask import AVAILABLE_ACTION_TYPES, is_legal_name, ontask_prefs
from ontask.forms import RestrictedFileField

SUFFIX_LENGTH = 512

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
FIELD_PREFIX = '___ontask___select_'


class ActionUpdateForm(forms.ModelForm):
    """Basic class to edit name and description."""

    def __init__(self, *args, **kwargs):
        """Store user and wokflow."""
        self.user = kwargs.pop(str('workflow_user'), None)
        self.workflow = kwargs.pop(str('action_workflow'), None)
        super().__init__(*args, **kwargs)

    class Meta(object):
        """Select Action and the two fields."""

        model = Action
        fields = ('name', 'description_text')


class ActionForm(ActionUpdateForm):
    """Edit name, description and action type."""

    def __init__(self, *args, **kargs):
        """Adjust widget choices depending on action type."""
        super().__init__(*args, **kargs)

        at_field = self.fields['action_type']
        at_field.widget.choices = AVAILABLE_ACTION_TYPES
        # Remove those actions that are not available
        if len(AVAILABLE_ACTION_TYPES) == 1:
            # There is only one type of action. No need to generate the field.
            # Set to value and hide
            at_field.widget = forms.HiddenInput()
            at_field.initial = AVAILABLE_ACTION_TYPES[0][0]

    class Meta(ActionUpdateForm.Meta):
        """Select action and the three fields."""

        model = Action
        fields = ('name', 'description_text', 'action_type')


class ActionDescriptionForm(forms.ModelForm):
    """Form to edit the description of an action."""

    class Meta(object):
        """Select model and the description field."""

        model = Action
        fields = ('description_text',)


class FilterForm(forms.ModelForm):
    """Form to read information about a filter.

    The required property of the formula field is set to False because it is
    enforced in the server.
    """

    def __init__(self, *args, **kwargs):
        """Adjust formula field parameters to use QueryBuilder."""
        super().__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

    class Meta(object):
        """Select model and fields."""

        model = Condition
        fields = ('description_text', 'formula')


class ConditionForm(forms.ModelForm):
    """Form to read information about a condition.

    The same as the filter but we need to enforce that the name is a valid
    variable name
    """

    def __init__(self, *args, **kwargs):
        """Adjust formula field to use the QueryBuilder."""
        super().__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

        # Remember the condition name to perform content substitution
        self.old_name = None
        with contextlib.suppress(AttributeError):
            self.old_name = self.instance.name

    def clean(self):
        """Check that data is not empty."""
        form_data = super().clean()

        if not form_data.get('name'):
            self.add_error('name', _('Name cannot be empty'))
            return form_data

        msg = is_legal_name(form_data['name'])
        if msg:
            self.add_error('name', msg)

        return form_data

    class Meta(object):
        """Define condition model and select fields."""

        model = Condition
        fields = ('name', 'description_text', 'formula')


class ActionImportForm(forms.Form):
    """Form to edit information to import an action."""

    # Action name
    name = forms.CharField(
        max_length=ACTION_NAME_LENGTH,
        strip=True,
        required=True,
        label='Name',
    )

    upload_file = RestrictedFileField(
        max_upload_size=int(ontask_prefs.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask_prefs.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File'),
        help_text=_('File containing a previously exported action'),
    )

    def __init__(self, form_data, *args, **kwargs):
        """Store workflow and user parameters."""
        self.workflow = kwargs.pop('workflow')
        self.user = kwargs.pop('user')

        super().__init__(form_data, *args, **kwargs)

    def clean(self):
        """Verify that the name of the action is not present already."""
        form_data = super().clean()

        name_exists = self.workflow.actions.filter(
            workflow__user=self.user, name=form_data['name'],
        ).exists()
        if name_exists:
            # There is an action with this name. Return error.
            self.add_error(
                'name',
                _('An action with this name already exists'))

        return form_data
