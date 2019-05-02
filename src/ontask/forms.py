# -*- coding: utf-8 -*-


import pytz
from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

import ontask.ontask_prefs

dateTimeWidgetOptions = {
    'locale': settings.LANGUAGE_CODE,
    'icons': {'time': 'fa fa-clock-o',
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

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = int(ontask.ontask_prefs.MAX_UPLOAD_SIZE)
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        try:
            if data.content_type in self.content_types:
                if data.size > self.max_upload_size:
                    raise forms.ValidationError(
                        _('File size must be under %(max)s. Current file '
                          'size is %(current)s.')
                        % ({
                            'max': filesizeformat(self.max_upload_size),
                            'current': filesizeformat(data.size)
                        }))
            else:
                raise forms.ValidationError(
                    _('File type (%s) is not supported.') % data.content_type)
        except AttributeError:
            pass

        return data


