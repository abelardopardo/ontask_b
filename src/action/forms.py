# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from tinymce.widgets import TinyMCE


from .models import Action, Condition


class ActionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('workflow_user', None)
        self.workflow = kwargs.pop('action_workflow', None)
        super(ActionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Action
        fields = ('name', 'description_text',)


class EditActionForm(forms.ModelForm):

    # content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 50}))

    content = forms.CharField(
        widget=TinyMCE(),
        initial='{% comment %} Write your conditional text in here {% comment %}',
        label='')

    class Meta:
        model = Action
        fields = ('content',)


class ConditionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('workflow_user', None)
        super(ConditionForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

    def clean(self):
        data = super(ConditionForm, self).clean()

        if ' ' in data['name'] or '-' in data['name']:
            self.add_error(
                'name',
                'Condition names can only have letters, numbers and _'
            )
            return data

        # if data['name'] in self.keys:
        #     self.add_error(
        #         'key',
        #         'Name has to be different from the existing ones.')
        #     return data
        #
        return data

    class Meta:
        model = Condition
        fields = ('name', 'description_text', 'formula')
        # widgets = {'formula': forms.HiddenInput()}
