# -*- coding: utf-8 -*-

"""Forms to edit action content.

EditActionOutForm: Form to process content action_out (Base class)

EditActionIn: Form to process action in elements
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteInplaceWidget

from action.forms import field_prefix
from action.models import Action
from ontask.forms import column_to_field


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
        self.tuples = kargs.pop('tuples', default=None)
        self.context = kargs.pop('context', default=None)
        self.form_values = kargs.pop('values', default=None)
        self.show_key = kargs.pop('show_key', defaut=False)
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

            field_name = field_prefix + '{0}'.format(idx)
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
