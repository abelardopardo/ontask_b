# -*- coding: utf-8 -*-


from builtins import next
from builtins import str
# from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

import ontask.ontask_prefs
from core.widgets import OnTaskDateTimeInput

# dateTimeOptions = {
#     'weekStart': 1,  # Start week on Monday
#     'minuteStep': 5,  # Minute step
# }


class RestrictedFileField(forms.FileField):

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = str(ontask.ontask_prefs.MAX_UPLOAD_SIZE)
        super(RestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedFileField, self).clean(*args, **kwargs)
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


def column_to_field(col, initial=None, required=False, label=None):
    """
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
        choices = [(x, x) for x in col.categories]
        initial = next((v for x, v in enumerate(choices) if v[0] == initial),
                       ('', '---'))

        # If the column is of type string, allow always the empty value
        if col.data_type == 'string':
            choices.insert(0, ('', '---'))

        return forms.ChoiceField(choices=choices,
                                 required=required,
                                 initial=initial,
                                 label=label)

    # Column is open value
    if col.data_type == 'string':
        if not initial:
            initial = ''
        if not col.categories:
            # The field does not have any categories
            return forms.CharField(initial=initial,
                                   label=label,
                                   required=required)

    elif col.data_type == 'integer':
        return forms.IntegerField(initial=initial,
                                  label=label,
                                  required=required)

    elif col.data_type == 'double':
        return forms.FloatField(initial=initial,
                                label=label,
                                required=required)

    elif col.data_type == 'boolean':
        return forms.BooleanField(initial=initial,
                                  label=label,
                                  required=required)

    elif col.data_type == 'datetime':
        return forms.DateTimeField(
            initial=initial,
            label=label,
            required=required,
            widget=OnTaskDateTimeInput()
            # widget=DateTimeWidget(options=dateTimeOptions,
            #                       usel10n=True,
            #                       bootstrap_version=3),
        )
    else:
        raise Exception(_('Unable to process datatype '), col.data_type)
