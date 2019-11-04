# -*- coding: utf-8 -*-

"""Generic forms to be used in various placdes in the platform."""
from typing import Dict, Optional, Any, List

import pytz
from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from ontask.settings import MAX_UPLOAD_SIZE

date_time_widget_options = {
    'locale': settings.LANGUAGE_CODE,
    'icons': {
        'time': 'fa fa-clock-o',
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
                        form_data.content_type),
                )
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
        super().__init__(*args, **kwargs)

    def get_payload_field(
        self,
        key: str,
        default: Optional[Any] = None
    ) -> Any:
        return self.__form_info.get(key, default)

    def set_field_from_dict(self, field_name: str):
        """Initialize the field with the value in __form_info it it exists.

    :param form: Form object containing all the fields

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
        if field_value:
            self.__form_info[field_name] = field_value
        else:
            self.__form_info[field_name] = self.cleaned_data[field_name]

    def store_fields_in_dict(self, field_pairs):
        """Store the list of (field_name, field_value=None) in the dict.

        :param field_pairs: List of field names to store in the dictionary.
        """
        for field_name, field_default in field_pairs:
            self.store_field_in_dict(field_name, field_default)
