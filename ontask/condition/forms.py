# -*- coding: utf-8 -*-

"""Forms to process condition related fields."""
from typing import Dict

from django import forms
from django.utils.translation import ugettext_lazy as _

from ontask import is_legal_name, models


class FilterForm(forms.ModelForm):
    """Form to read/write information about a filter."""

    action = None
    old_name = None

    def __init__(self, *args, **kwargs):
        """Adjust formula field parameters to use QueryBuilder."""
        self.action = kwargs.pop('action')

        super().__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

    class Meta:
        """Select model and fields."""

        model = models.Condition
        fields = ('description_text', 'formula')
        widgets = {'formula': forms.HiddenInput()}


class ConditionForm(FilterForm):
    """Form to read information about a condition.

    The same as the filter but we need to enforce that the name is a valid
    variable name
    """

    def __init__(self, *args, **kwargs):
        """Remember the old name."""
        super().__init__(*args, **kwargs)

        # Remember the condition name to perform content substitution
        if self.instance.name:
            self.old_name = self.instance.name

    def clean(self) -> Dict:
        """Check that data is not empty."""
        form_data = super().clean()

        name = form_data.get('name')
        if not name:
            self.add_error('name', _('Name cannot be empty'))
            return form_data

        msg = is_legal_name(form_data['name'])
        if msg:
            self.add_error('name', msg)

        # Check if the name already exists
        name_exists = self.action.conditions.filter(
            name=name,
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already a condition with this name.'),
            )

        # Check that the name does not collide with other attribute or column
        if name in self.action.workflow.get_column_names():
            self.add_error(
                'name',
                _('The workflow has a column with this name.'),
            )

        # New condition name does not collide with attribute names
        if name in list(self.action.workflow.attributes.keys()):
            self.add_error(
                'name',
                _('The workflow has an attribute with this name.'),
            )

        return form_data

    class Meta(FilterForm.Meta):
        """Select name as extra field."""

        fields = ('name', 'description_text', 'formula')
