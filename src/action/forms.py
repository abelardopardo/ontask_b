# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django import forms
from django_summernote.widgets import SummernoteInplaceWidget

from .models import Action, Condition


class ActionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(str('workflow_user'), None)
        self.workflow = kwargs.pop(str('action_workflow'), None)
        super(ActionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Action
        fields = ('name', 'description_text',)


class EditActionForm(forms.ModelForm):
    """
    Main class to edit an action. The main element is the text editor (
    currently using summernote).
    """
    content = forms.CharField(
        widget=SummernoteInplaceWidget(),
        initial='{% comment %} Write your conditional ' +
                'text in here {% comment %}',
        label='')

    class Meta:
        model = Action
        fields = ('content',)


class FilterForm(forms.ModelForm):
    """
    Form to read information about a filter. The required property of the
    formula field is set to False because it is enforced in the server.
    """
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

    class Meta:
        model = Condition
        fields = ('name', 'description_text', 'formula')


class ConditionForm(FilterForm):
    """
    Form to read information about a condition. The same as the filter but we
    need to enforce that the name is a valid variable name
    """

    def __init__(self, *args, **kwargs):

        super(ConditionForm, self).__init__(*args, **kwargs)

        # Remember the condition name to perform content substitution
        self.old_name = None,
        if hasattr(self, 'instance'):
            self.old_name = self.instance.name

    def clean(self):
        data = super(ConditionForm, self).clean()

        if ' ' in data['name'] or '-' in data['name']:
            self.add_error(
                'name',
                'Condition names can only have letters, numbers and _'
            )
            return data

        return data


class EnableURLForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ('serve_enabled',)
