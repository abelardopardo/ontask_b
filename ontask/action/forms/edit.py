# -*- coding: utf-8 -*-

"""Forms to edit action content.

EditActionOutForm: Form to process content action_out (Base class)

EditActionIn: Form to process action in elements
"""
from typing import Any, Dict, List, Tuple

from django import forms
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteInplaceWidget

from ontask import models
from ontask.action import evaluate
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX, column_to_field


class EditActionOutForm(forms.ModelForm):
    """Main class to edit an action out."""

    text_content = forms.CharField(label='', required=False)

    def __init__(self, *args, **kargs):
        """Adjust field parameters for content and target_URL."""
        super().__init__(*args, **kargs)

        # Personalized text, canvas email
        if (
            self.instance.action_type == models.Action.PERSONALIZED_TEXT
            or self.instance.action_type == models.Action.RUBRIC_TEXT
            or self.instance.action_type == models.Action.EMAIL_REPORT
        ):
            self.fields['text_content'].widget = SummernoteInplaceWidget()

        # Add the Target URL field
        if (
            self.instance.action_type == models.Action.PERSONALIZED_JSON
            or self.instance.action_type == models.Action.JSON_REPORT
        ):
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
                        'placeholder': _('URL to send the JSON object'),
                    },
                ),
            )

            # Modify the content field so that it uses the TextArea
            self.fields['text_content'].widget = forms.Textarea(
                attrs={
                    'cols': 80,
                    'rows': 15,
                    'placeholder': _('Write a JSON object'),
                },
            )

        if self.instance.action_type == models.Action.PERSONALIZED_CANVAS_EMAIL:
            # Modify the content field so that it uses the TextArea
            self.fields['text_content'].widget = forms.Textarea(
                attrs={
                    'cols': 80,
                    'rows': 15,
                    'placeholder': _('Write a plain text message'),
                },
            )

    def clean(self) -> Dict:
        """Verify that the template text renders correctly."""
        form_data = super().clean()
        try:
            evaluate.render_action_template(
                form_data['text_content'],
                {},
                self.instance)
        except Exception as exc:
            # Pass the django exception as an error form
            self.add_error(None, str(exc))

        return form_data

    class Meta:
        """Select action and the content field only."""

        model = models.Action
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

            field_name = ONTASK_UPLOAD_FIELD_PREFIX + '{0}'.format(idx)
            the_field = column_to_field(
                cc_item.column,
                self.form_values[idx],
                label=cc_item.column.description_text)
            self.fields[field_name] = the_field

            if cc_item.column.is_key or not cc_item.changes_allowed:
                the_field.widget.attrs['readonly'] = 'readonly'
                the_field.disabled = True
            else:
                # We are adding at least one field to be filled
                self.is_empty = False

    def get_key_value_pairs(self) -> Tuple[List, List, str, Any]:
        """Extract key/value pairs and primary key/value.

        :return: Tuple with List[keys], List[values], where_field, where_value
        """
        keys = []
        values = []
        where_field = None
        where_value = None
        # Create the SET name = value part of the query
        for idx, colcon in enumerate(self.tuples):
            if colcon.column.is_key and not self.show_key:
                # If it is a learner request and a key column, skip
                continue

            # Skip the element if there is a condition and it is false
            if colcon.condition and not self.context[colcon.condition.name]:
                continue

            field_value = self.cleaned_data[
                ONTASK_UPLOAD_FIELD_PREFIX + '{0}'.format(idx)]
            if colcon.column.is_key:
                # Remember one unique key for selecting the row
                where_field = colcon.column.name
                where_value = field_value
                continue

            keys.append(colcon.column.name)
            values.append(field_value)

        return keys, values, where_field, where_value
