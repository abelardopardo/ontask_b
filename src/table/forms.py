# -*- coding: utf-8 -*-


from builtins import next, object

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import View


class ViewAddForm(forms.ModelForm):

    # Columns to combine
    columns = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, data, *args, **kwargs):
        self.workflow = kwargs.pop('workflow', None)

        super().__init__(data, *args, **kwargs)

        # Rename some of the fields
        self.fields['name'].label = _('View name')
        self.fields['columns'].label = _('Columns to show')
        self.fields['description_text'].label = _('View Description')

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

        # The queryset for the columns must be extracted from the workflow
        self.fields['columns'].queryset = self.workflow.columns.all()

    def clean(self):

        data = super().clean()

        if data['columns'].count() == 0:
            self.add_error(
                None,
                _('The view needs at least one column to show')
            )

        if not next((x for x in data['columns'] if x.is_key), None):
            self.add_error(
                None,
                _('There needs to be at least one key column')
            )

        return data

    class Meta(object):
        model = View
        fields = ['name',
                  'description_text',
                  'formula',
                  'columns']
