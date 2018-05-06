# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django import forms

from .models import View


class ViewAddForm(forms.ModelForm):

    # Columns to combine
    columns = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, data, *args, **kwargs):
        self.workflow = kwargs.pop('workflow', None)

        super(ViewAddForm, self).__init__(data, *args, **kwargs)

        # Rename some of the fields
        self.fields['name'].label = 'View name'
        self.fields['columns'].label = 'Columns to show'
        self.fields['description_text'].label = 'View Description'

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

        # The queryset for the columns must be extracted from the workflow
        self.fields['columns'].queryset = self.workflow.columns.all()

    def clean(self):

        data = super(ViewAddForm, self).clean()

        if data['columns'].count() == 0:
            self.add_error(
                None,
                'The view needs at least one column to show'
            )

        if not next((x for x in data['columns'] if x.is_key), None):
            self.add_error(
                None,
                'There needs to be at least one key column'
            )

        return data

    class Meta:
        model = View
        fields = ['name',
                  'description_text',
                  'formula',
                  'columns']