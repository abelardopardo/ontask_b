# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django import forms
from django_summernote.widgets import SummernoteInplaceWidget

from .models import Action, Condition
from ontask.forms import column_to_field

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
field_prefix = '___ontask___select_'


class ActionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(str('workflow_user'), None)
        self.workflow = kwargs.pop(str('action_workflow'), None)
        super(ActionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Action
        fields = ('name', 'description_text',)


class EditActionOutForm(forms.ModelForm):
    """
    Main class to edit an action out. The main element is the text editor (
    currently using summernote).
    """
    content = forms.CharField(
        widget=SummernoteInplaceWidget(),
        label='')

    class Meta:
        model = Action
        fields = ('content',)


# Form to select a subset of the columns
class EditActionInForm(forms.ModelForm):
    """
    Main class to edit an action in . The main element is the text editor (
    currently using summernote).
    """

    def __init__(self, *args, **kwargs):

        self.columns = kwargs.pop('columns', [])
        self.selected = kwargs.pop('selected', [])

        super(EditActionInForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['filter'].required = False

        # Filter should be hidden.
        self.fields['filter'].widget = forms.HiddenInput()

        # Create as many fields as the given columns
        for idx in range(len(self.columns)):

            self.fields[field_prefix + '%s' % idx] = forms.BooleanField(
                initial=self.selected[idx],
                label='',
                required=False,
            )

    def clean(self):
        cleaned_data = super(EditActionInForm, self).clean()

        selected_list = [
            cleaned_data.get(field_prefix + '%s' % i, False)
            for i in range(len(self.columns))
        ]

        # Check if at least a unique column has been selected
        both_lists = zip(selected_list, self.columns)
        if not any([a and b.is_key for a, b in both_lists]):
            self.add_error(None, 'No key column specified',)

    class Meta:
        model = Action
        fields = ('filter',)


# Form to enter values in a row
class EnterActionIn(forms.Form):

    def __init__(self, *args, **kargs):

        # Store the instance
        self.columns = kargs.pop('columns', None)
        self.values = kargs.pop('values', None)

        super(EnterActionIn, self).__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.values:
            self.values = [None] * len(self.columns)

        for idx, column in enumerate(self.columns):
            self.fields[field_prefix + '%s' % idx] = \
                column_to_field(column, self.values[idx])

            if column.is_key:
                self.fields[field_prefix + '%s' % idx].widget.attrs[
                    'readonly'
                ] = 'readonly'
                self.fields[field_prefix + '%s' % idx].disabled = True


class FilterForm(forms.ModelForm):
    """
    Form to read information about a filter. The required property of the
    formula field is set to False because it is enforced in the server.
    """
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

        # Filter should be hidden.
        self.fields['formula'].widget = forms.HiddenInput()

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
