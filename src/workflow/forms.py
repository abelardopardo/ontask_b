# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from .models import Workflow


class WorkflowForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('workflow_user', None)
        super(WorkflowForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Workflow
        fields = ('name', 'description_text',)


class AttributeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.form_fields = kwargs.pop('form_fields')
        super(AttributeForm, self).__init__(*args, **kwargs)

        # Create the set of fields
        for key, val_field, val in self.form_fields:
            # Field for the key
            self.fields[key] = forms.CharField(
                max_length=1024,
                initial=key,
                strip=True,
                label='')

            # Field for the value
            self.fields[val_field] = forms.CharField(
                max_length=1024,
                initial=val,
                label='')

    def clean(self):
        data = super(AttributeForm, self).clean()

        new_keys = [data[x] for x, _, _ in self.form_fields]

        # Check that there were not duplicate keys given
        if len(set(new_keys)) != len(new_keys):
            raise forms.ValidationError(
                'Repeated names are not allowed'
            )

        return data


class AttributeItemForm(forms.Form):

    # Key field
    key = forms.CharField(max_length=1024,
                          strip=True,
                          required=True,
                          label='Name')

    # Field for the value
    value = forms.CharField(max_length=1024,
                           label='Value')

    def __init__(self, *args, **kwargs):
        self.keys = kwargs.pop('keys')
        super(AttributeItemForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(AttributeItemForm, self).clean()

        if ' ' in data['key'] or '-' in data['key']:
            self.add_error(
                'key',
                'Attribute names can only have letters, numbers and _'
            )
            return data

        if data['key'] in self.keys:
            self.add_error(
                'key',
                'Name has to be different from the existing ones.')
            return data

        return data
