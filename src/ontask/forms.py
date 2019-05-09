# -*- coding: utf-8 -*-

"""Generic forms to be used in various placdes in the platform."""

import pytz
from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from ontask.ontask_prefs import MAX_UPLOAD_SIZE

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
