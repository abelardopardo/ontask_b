# -*- coding: utf-8 -*-

"""Forms to process attributes and sharing."""

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from ontask.apps.action.models import Condition
from ontask import is_legal_name

CHAR_FIELD_SIZE = 1024


class AttributeItemForm(forms.Form):
    """Form to get a key/value pair as attribute."""

    key = forms.CharField(
        max_length=CHAR_FIELD_SIZE,
        strip=True,
        required=True,
        label=_('Name'))

    # Field for the value
    attr_value = forms.CharField(max_length=CHAR_FIELD_SIZE, label='Value')

    def __init__(self, *args, **kwargs):
        """Set keys and values."""
        self.keys = kwargs.pop('keys')
        self.workflow = kwargs.pop('workflow', None)

        key = kwargs.pop('key', '')
        att_value = kwargs.pop('value', '')

        super().__init__(*args, **kwargs)

        self.fields['key'].initial = key
        self.fields['attr_value'].initial = att_value

    def clean(self):
        """Check that the name is correct and is not duplicated."""
        form_data = super().clean()

        attr_name = form_data['key']

        # Name is legal
        msg = is_legal_name(attr_name)
        if msg:
            self.add_error('key', msg)
            return form_data

        if attr_name in self.keys:
            self.add_error(
                'key',
                _('Name has to be different from all existing ones.'))
            return form_data

        # Enforce the property that Attribute names, column names and
        # condition names cannot overlap.
        if attr_name in self.workflow.get_column_names():
            self.add_error(
                'key',
                _('There is a column with this name. Please change.'),
            )
            return form_data

        # Check if there is a condition with that name
        if (
            Condition.objects.filter(
                action__workflow=self.workflow,
                name=attr_name,
            ).exists()
        ):
            self.add_error(
                'key',
                _('There is a condition already with this name.'),
            )
            return form_data

        return form_data


class SharedForm(forms.Form):
    """Form to ask for a user email to add to those sharing the workflow.

    The form uses two parameters:

    :param user: The user making the request (to detect self-sharing)

    :param workflow: The workflow to share (to detect users already in the
     list)
    """

    user_email = forms.CharField(
        max_length=CHAR_FIELD_SIZE,
        strip=True,
        label=_('User email'))

    def __init__(self, *args, **kwargs):
        """Set the request user, workflow."""
        self.request_user = kwargs.pop('user', None)
        self.workflow = kwargs.pop('workflow')
        self.user_obj = None

        super().__init__(*args, **kwargs)

    def clean(self):
        """Check that the request has the correct user."""
        form_data = super().clean()

        self.user_obj = get_user_model().objects.filter(
            email__iexact=form_data['user_email'],
        ).first()
        if not self.user_obj:
            self.add_error('user_email', _('User not found'))
            return form_data

        if self.user_obj == self.request_user:
            self.add_error(
                'user_email',
                _('You do not need to add yourself to the share list'))

        if self.user_obj in self.workflow.shared.all():
            self.add_error('user_email', _('User already in the list'))

        return form_data
