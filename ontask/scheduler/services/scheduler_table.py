# -*- coding: utf-8 -*-

"""Service to produce the table with the scheduler objects."""
from cron_descriptor import CasingTypeEnum, ExpressionDescriptor
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A
import django_tables2 as tables

from ontask import models
from ontask.core.tables import OperationsColumn


class ScheduleActionTable(tables.Table):
    """Table to show the email actions scheduled for a workflow."""

    operations = OperationsColumn(
        verbose_name='',
        orderable=False,
        template_file='scheduler/includes/partial_scheduler_operations.html',
        template_context=lambda record: {'id': record.id},
    )

    name = tables.Column(verbose_name=_('Name'))

    operation_type = tables.Column(verbose_name=_('Type'))

    execute = tables.DateTimeColumn(verbose_name=_('From'))

    frequency = tables.Column(verbose_name=_('Frequency'))

    execute_until = tables.DateTimeColumn(verbose_name=_('Until'))

    enabled = tables.BooleanColumn(
        verbose_name=_('Enabled?'),
        default=True,
        accessor=A('task__enabled'))

    status = tables.Column(
        verbose_name=_('Status'),
        accessor=A('get_status_display'))

    @staticmethod
    def render_operation_type(record):
        """Create the string with the operation type."""
        return models.Log.LOG_TYPES[record.operation_type]

    @staticmethod
    def render_frequency(record):
        """Create the cron description."""
        if not record.frequency:
            return ''
        return str(ExpressionDescriptor(
            record.frequency,
            casing_type=CasingTypeEnum.LowerCase))

    @staticmethod
    def render_enabled(record):
        """Render the is enabled as a checkbox."""
        return render_to_string(
            'scheduler/includes/partial_scheduler_enable.html',
            context={'record': record},
            request=None)

    @staticmethod
    def render_status(record):
        """Render status as a link."""
        log_item = record.last_executed_log
        if not log_item:
            return record.get_status_display()

        # At this point, the object is not pending. Produce a link
        return format_html(
            '<a class="spin" href="{0}">{1}</a>',
            reverse('logs:page_view', kwargs={'pk': log_item.id}),
            record.get_status_display())

    class Meta:
        """Choose model, fields and sequence in the table."""

        model = models.ScheduledOperation

        fields = (
            'name',
            'operation_type',
            'execute',
            'frequency',
            'execute_until',
            'status')

        sequence = (
            'operations',
            'name',
            'operation_type',
            'execute',
            'frequency',
            'execute_until',
            'enabled',
            'status')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'scheduler-table'}
