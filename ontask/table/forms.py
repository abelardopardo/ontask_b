# -*- coding: utf-8 -*-

"""Forms to manage Views."""
from builtins import next
from typing import Dict

from django import forms
from django.utils.translation import ugettext_lazy as _

from ontask import models


class ViewAddForm(forms.ModelForm):
    """Form to add a view."""

    # Columns to combine
    columns = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, data, *args, **kwargs):  # noqa: Z110
        """Initialize the object, store the workflow and rename fields."""
        self.workflow = kwargs.pop('workflow', None)

        super().__init__(data, *args, **kwargs)

        # Rename some of the fields
        self.fields['name'].label = _('View name')
        self.fields['description_text'].label = _('View Description')
        self.fields['columns'].label = _('Columns to show')

        # Required enforced in the server (not in the browser)
        self.fields['_formula'].required = False

        # Filter should be hidden.
        self.fields['_formula'].widget = forms.HiddenInput()

        # The queryset for the columns must be extracted from the workflow
        self.fields['columns'].queryset = self.workflow.columns.all()

    def clean(self) -> Dict:
        """Check if three properties in the form.

        1) Number of columns is not empty

        2) There is at least one key column

        3) There is no view with that name.
        """
        form_data = super().clean()

        if form_data['columns'].count() == 0:
            self.add_error(
                None,
                _('The view needs at least one column to show'))

        if not next(
            (col for col in form_data['columns'] if col.is_key),
            None,
        ):
            self.add_error(
                None,
                _('There needs to be at least one key column'))

        # Check if the name already exists
        name_exists = self.workflow.views.filter(
            name=self.cleaned_data['name'],
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already a view with this name.'),
            )

        return form_data

    class Meta:
        """Define models and fields to consider."""

        model = models.View
        fields = ['name', 'description_text', '_formula', 'columns']
