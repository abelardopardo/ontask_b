# -*- coding: utf-8 -*-

"""Forms to edit action content.

EditActionOutForm: Form to process content action_out (Base class)

EditActionIn: Form to process action in elements
"""
from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteInplaceWidget

from ontask.apps.action.forms import FIELD_PREFIX
from ontask.apps.action.models import Action
from ontask.forms import date_time_widget_options


def column_to_field(col, initial=None, required=False, label=None):
    """Generate form fields to enter values for a column.

    Function that given the description of a column it generates the
    appropriate field to be included in a form
    :param col: Column object to use as the basis to create the field
    :param initial: Initial value for the field
    :param required: flag to generate the field with the required attribute
    :param label: Value to overwrite the label attribute
    :return: Field object
    """
    # If no label is given, take the column name
    if not label:
        label = col.name

    if col.categories:
        # Column has a finite set of prefixed values
        choices = [(value_cat, value_cat) for value_cat in col.categories]
        initial = next(
            (choice for choice in choices if initial == choice),
            ('', '---'))

        # If the column is of type string, allow always the empty value
        if col.data_type == 'string':
            choices.insert(0, ('', '---'))

        return forms.ChoiceField(
            choices=choices,
            required=required,
            initial=initial,
            label=label)

    distributor = {
        'string': forms.CharField,
        'integer': forms.IntegerField,
        'double': forms.FloatField,
        'boolean': forms.BooleanField,
        'datetime': forms.DateTimeField,
    }

    new_field = distributor[col.data_type](
        initial=initial,
        label=label,
        required=required)

    # Column is open value
    if col.data_type == 'string' and not initial:
        new_field.initial = ''

    if col.data_type == 'datetime':
        new_field.widget = DateTimePickerInput(
            options=date_time_widget_options)

    return new_field


class EditActionOutForm(forms.ModelForm):
    """Main class to edit an action out."""

    text_content = forms.CharField(label='', required=False)

    def __init__(self, *args, **kargs):
        """Adjust field parameters for content and target_URL."""
        super().__init__(*args, **kargs)

        # Personalized text, canvas email
        if self.instance.action_type == Action.personalized_text:
            self.fields['text_content'].widget = SummernoteInplaceWidget()

        # Add the Target URL field
        if self.instance.action_type == Action.personalized_json:
            # Add the target_url field
            self.fields['target_url'] = forms.CharField(
                initial=self.instance.target_url,
                label=_('Target URL'),
                strip=True,
                required=False,
                widget=forms.Textarea(
                    attrs={
                        'rows': 1,
                        'cols': 80,
                        'placeholder': _('URL to send the personalized JSON'),
                    },
                ),
            )

        if self.instance.action_type == Action.personalized_json:
            # Modify the content field so that it uses the TextArea
            self.fields['text_content'].widget = forms.Textarea(
                attrs={
                    'cols': 80,
                    'rows': 15,
                    'placeholder': _('Write a JSON object'),
                },
            )

        if self.instance.action_type == Action.personalized_canvas_email:
            # Modify the content field so that it uses the TextArea
            self.fields['text_content'].widget = forms.Textarea(
                attrs={
                    'cols': 80,
                    'rows': 15,
                    'placeholder': _('Write a plain text message'),
                },
            )

    class Meta(object):
        """Select action and the content field only."""

        model = Action
        fields = ['text_content']


class EnterActionIn(forms.Form):
    """Form to enter values in a row."""

    def __init__(self, *args, **kargs):
        """Store parameters and adjust questions, columns, etc."""
        # Store the parameters
        self.tuples = kargs.pop('tuples', None)
        self.context = kargs.pop('context', None)
        self.form_values = kargs.pop('values', None)
        self.show_key = kargs.pop('show_key', None)
        self.is_empty = True

        super().__init__(*args, **kargs)

        # If no initial values have been given, replicate a list of Nones
        if not self.form_values:
            self.form_values = [None] * len(self.tuples)

        for idx, cc_item in enumerate(self.tuples):
            # Skip the key columns if flag is true
            if not self.show_key and cc_item.column.is_key:
                continue

            # Skip the element if there is a condition and it is false
            if cc_item.condition and not self.context[cc_item.condition.name]:
                continue

            field_name = FIELD_PREFIX + '{0}'.format(idx)
            the_field = column_to_field(
                cc_item.column,
                self.form_values[idx],
                label=cc_item.column.description_text,
            )
            self.fields[field_name] = the_field

            if cc_item.column.is_key:
                the_field.widget.attrs['readonly'] = 'readonly'
                the_field.disabled = True
            else:
                # We are adding at least one field to be filled
                self.is_empty = False
