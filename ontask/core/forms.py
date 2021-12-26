# -*- coding: utf-8 -*-

"""Generic forms to be used in various placdes in the platform."""
from typing import Any, List, Optional

from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
import pytz

from ontask.settings import MAX_UPLOAD_SIZE

DATE_TIME_WIDGET_OPTIONS = {
    'locale': settings.LANGUAGE_CODE,
    'icons': {
        'time': 'fa fa-clock',
        'date': 'fa fa-calendar',
        'up': 'fa fa-angle-up',
        'down': 'fa fa-angle-down',
        'previous': 'fa fa-angle-left',
        'next': 'fa fa-angle-right',
        'today': 'fa fa-crosshairs',
        'clear': 'fa fa-trash',
        'close': 'fa fa-times-circle'},
    'showTodayButton': True,
    'showClear': True,
    'showClose': True,
    'calendarWeeks': True,
    'timeZone': str(pytz.timezone(settings.TIME_ZONE)),
}


class RestrictedFileField(forms.FileField):
    """Restrict the File Field with a size."""

    def __init__(self, *args, **kwargs):
        """Initalise the content types and the max upload size."""
        self.content_types = kwargs.pop('content_types', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = int(MAX_UPLOAD_SIZE)
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Verify that type content and size are correct."""
        form_data = super().clean(*args, **kwargs)
        try:
            if form_data.content_type in self.content_types:
                if form_data.size > self.max_upload_size:
                    raise forms.ValidationError(
                        _(
                            'File size must be under %(max)s. Current file '
                            + 'size is %(current)s.').format(
                            filesizeformat(self.max_upload_size),
                            filesizeformat(form_data.size),
                        ),
                    )
            else:
                raise forms.ValidationError(_(
                    'File type ({0}) is not supported.').format(
                    form_data.content_type))
        except AttributeError:
            return form_data

        return form_data


class FormWithPayload(forms.Form):
    """Form that has a method to initialize fields based on a Dict.

    The constructor receives a form_info dictionary that is used to initialize
    the fields in the form.
    """

    def __init__(self, *args, **kwargs):
        self.__form_info = kwargs.pop('form_info', {})
        self.action = kwargs.pop('action', None)
        kwargs.pop('columns', None)
        kwargs.pop('connection', None)
        super().__init__(*args, **kwargs)

    def get_payload_field(
        self,
        key: str,
        default: Optional[Any] = None
    ) -> Any:
        """"Get a field stored in the payload."""
        return self.__form_info.get(key, default)

    def set_field_from_dict(self, field_name: str):
        """Initialize the field with the value in __form_info it it exists.

    :param field_name: Field to be initialized
    :return: Effect reflected in the field within the form.
    """
        if field_name in self.__form_info:
            self.fields[field_name].initial = self.__form_info[field_name]

    def set_fields_from_dict(self, field_names: List[str]):
        """Set the list of field_names as values in fields

        :param field_names: List of field_names to use
        """
        for field_name in field_names:
            self.set_field_from_dict(field_name)

    def store_field_in_dict(
        self,
        field_name: str,
        field_value: Optional[Any] = None
    ):
        """Store the value."""
        if field_value is not None:
            self.__form_info[field_name] = field_value
        else:
            self.__form_info[field_name] = self.cleaned_data[field_name]

    def store_fields_in_dict(self, field_pairs):
        """Store the list of (field_name, field_value=None) in the dict.

        :param field_pairs: List of field names to store in the dictionary.
        """
        for field_name, field_default in field_pairs:
            self.store_field_in_dict(field_name, field_default)


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
            (choice for choice in choices if initial == choice[0]),
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
            options=DATE_TIME_WIDGET_OPTIONS)

    return new_field
