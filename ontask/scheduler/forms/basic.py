"""Forms for scheduling actions."""
from typing import Dict

from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core import forms as ontask_forms


class OnTaskCronWidget(forms.TextInput):
    """Widget to use with the jqCron to catch the cron parameter."""

    def render(self, name, value, attrs=None, renderer=None):
        """Add additional JS code."""
        super_text = super().render(name, value, attrs, renderer)

        return (
            '<div class="ontask-scheduler-frequency"></div><div '
            'style="display:none;">' + super_text + '</div>')


class ScheduleBasicForm(ontask_forms.FormWithPayload, forms.ModelForm):
    """Form to create/edit objects of the ScheduleAction.

    To be used for the various types of actions.
    """

    multiple_executions = forms.BooleanField(
        required=False,
        label=_('Multiple executions?'),
        help_text=_('Select if you want to execute multiple times.'))

    def __init__(self, *args, **kwargs):
        """Set item_column values."""
        self.workflow = kwargs.pop('workflow', None)
        super().__init__(*args, **kwargs)

        self.set_fields_from_dict([
            'name',
            'description_text',
            'execute_start',
            'frequency',
            'execute_until'])
        self.fields['execute_start'].initial = parse_datetime(
            self.get_payload_field('execute_start', ''))
        self.fields['execute_until'].initial = parse_datetime(
            self.get_payload_field('execute_until', ''))
        self.fields['frequency'].label = ''

        self.fields['multiple_executions'].initial = bool(
            self.instance.frequency)

        self.order_fields([
            'name',
            'description_text',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until'])

    def clean(self) -> Dict:
        """Verify that the date is correct."""
        form_data = super().clean()

        if not form_data['multiple_executions']:
            form_data['frequency'] = ''
            form_data['execute_until'] = ''

        self.store_fields_in_dict([
            ('name', None),
            ('description_text', None),
            ('execute_start', str(form_data['execute_start'])),
            ('frequency', form_data['frequency']),
            ('execute_until', str(form_data['execute_until']))])

        obj_name = self.workflow.scheduled_operations.filter(
            name=form_data['name']).exclude(id=self.instance.id)
        if obj_name.exists():
            self.add_error(
                'name',
                str(_('There is an operation scheduled with this name')))

        # The executed times must be correct
        diagnostic_msg = validate_crontab(
            self.cleaned_data.get('execute_start'),
            self.cleaned_data.get('frequency'),
            self.cleaned_data.get('execute_until'))

        if diagnostic_msg:
            self.add_error(None, diagnostic_msg)

        return form_data

    class Meta:
        """Define model, fields and widgets."""

        model = models.ScheduledOperation
        fields = (
            'name',
            'description_text',
            'execute_start',
            'frequency',
            'execute_until')
        widgets = {
            'execute_start': DateTimePickerInput(
                options=ontask_forms.DATE_TIME_WIDGET_OPTIONS),
            'frequency': OnTaskCronWidget(),
            'execute_until': DateTimePickerInput(
                options=ontask_forms.DATE_TIME_WIDGET_OPTIONS)}


class ScheduleBasicUpdateForm(ScheduleBasicForm):
    """Form to create/edit objects of the schedule/update action.

    To be used for Update actions.
    """

    dst_help = dataops_forms.SelectKeysForm.dst_help

    dst_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        strip=True,
        required=False,
        label=_('Key column in the existing table. '
                'Leave empty if uploading to empty workflow'),
        help_text=dst_help)

    src_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        strip=True,
        required=False,
        label=_('Key column in new table. '
                'Leave empty if uploading to empty workflow'))

    def __init__(self, *args, **kwargs):
        """Initialize all the fields"""
        super().__init__(*args, **kwargs)
        self.set_fields_from_dict(['dst_key', 'src_key', 'how_merge'])

        self.fields['how_merge'].required = False

    def clean(self) -> Dict:
        """Store the fields in the Form Payload"""
        form_data = super().clean()
        self.store_fields_in_dict([
            ('dst_key', None),
            ('src_key', None),
            ('how_merge', None)])

        # If the workflow has data, both keys have to be non-empty, the
        # first one needs to be a unique column, and the merge method cannot
        # be empty
        if not form_data['dst_key'] or not form_data['src_key']:
            self.add_error(
                None,
                _('The operation requires the names of two key columns.'))
        if not form_data['how_merge']:
            self.add_error(
                'how_merge',
                _('The operation requires a merge method.')
            )
        return form_data


class ScheduleSQLUploadForm(
    ScheduleBasicUpdateForm,
    dataops_forms.MergeForm,
    SQLRequestConnectionParam
):
    """Form to request info for the SQL scheduled upload

    Three blocks of information are requested:

    Block 1: Name, description, start -- frequency -- stop times

    Block 2: Parameters for the SQL connection

    Block 3: Parameters for the merge: Left/Right column + merge method
    """

    pass


class ScheduleCanvasUploadForm(
    ScheduleBasicUpdateForm,
    dataops_forms.MergeForm
):
    """Form to request info for the Canvas scheduled upload

    Two blocks of information are requested:

    Block 1: Name, description, start -- frequency -- stop times

    Block 2: Parameters for the merge: Left/Right column + merge method,

    Canvas Host is required only if more than one is specified.
    """

    canvas_course_id = forms.IntegerField(
        label=_('Canvas course id to retrieve the data.'),
        required=True,
        help_text=_(
            'This is an integer used by Canvas to uniquely identify a course'))

    def __init__(self, *args, **kwargs):
        """Modify certain field data."""
        super().__init__(*args, **kwargs)

        # Load the values in the payload
        self.set_fields_from_dict(['canvas_course_id'])

        # Adjustments to fields
        self.fields['how_merge'].required = True
        self.fields['execute_start'].required = True
        self.fields['src_key'].required = True
        self.fields['src_key'].label = _('Key column in the workflow table')
        self.fields['dst_key'].required = True
        self.fields['dst_key'].label = _('Key column in the external table')

        if len(settings.CANVAS_INFO_DICT) > 1:
            # Add the canvashost_url field if the system has more than one entry
            # point configured
            self.fields['canvashost_url'] = forms.ChoiceField(
                initial=self._FormWithPayload__form_info.get(
                    'canvashost_url', None),
                required=True,
                choices=[('', '---')] + [(key, key) for key in sorted(
                    settings.CANVAS_INFO_DICT.keys(),
                )],
                label=_('Canvas Host'),
                help_text=_('Name of the Canvas host to send the messages'))
            self.set_field_from_dict('canvashost_url')
        else:
            # Single Canvas config Add the value to the payload (no form field
            # required)
            self.store_field_in_dict(
                'canvashost_url',
                list(settings.CANVAS_INFO_DICT.keys())[0])

        self.order_fields([
            'name',
            'description_text',
            'canvashost_url',
            'canvas_course_id',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until',
            'dst_key',
            'src_key',
            'how_merge'])

    def clean(self) -> Dict:
        """Store the fields in the Form Payload"""
        form_data = super().clean()
        self.store_fields_in_dict([('canvas_course_id', None)])
        return form_data
