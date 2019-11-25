# -*- coding: utf-8 -*-

"""Service to produce the table with the scheduler objects."""
import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A

from ontask import models
from ontask.core.tables import OperationsColumn


class ScheduleActionTable(tables.Table):
    """Table to show the email actions scheduled for a workflow."""

    action = tables.LinkColumn(
        verbose_name=_('Action'),
        viewname='action:edit',
        text=lambda record: record.action.name,
        kwargs={'pk': A('action.id')},
        attrs={
            'a': {
                'class': 'spin',
                'data-toggle': 'tooltip',
                'title': _('Edit the action scheduled for execution'),
            },
        },
    )

    operations = OperationsColumn(
        verbose_name='',
        orderable=False,
        template_file='scheduler/includes/partial_scheduler_operations.html',
        template_context=lambda record: {'id': record.id},
    )

    name = tables.Column(verbose_name=_('Name'))

    execute = tables.DateTimeColumn(
        verbose_name=_('Scheduled'))

    execute_until = tables.DateTimeColumn(
        verbose_name=_('Until'))

    status = tables.Column(
        verbose_name=_('Status'),
        accessor=A('get_status_display'))

    def render_name(self, record):
        """Render name as link."""
        return format_html(
            '<a href="{0}" data-toggle="tooltip" title="{1}">{2}</a>',
            reverse(
                'scheduler:edit_scheduled_operation',
                kwargs={'pk': record.id}),
            _('Edit this scheduled operation'),
            record.name)

    def render_status(self, record):
        """Render status as a link."""
        log_item = record.last_executed_log
        if not log_item:
            return record.get_status_display()

        # At this point, the object is not pending. Produce a link
        return format_html(
            '<a class="spin" href="{0}">{1}</a>',
            reverse('logs:view', kwargs={'pk': log_item.id}),
            record.get_status_display())

    class Meta(object):
        """Choose model, fields and sequence in the table."""

        model = models.ScheduledOperation

        fields = (
            'name',
            'workflow',
            'action',
            'execute',
            'execute_until',
            'status')

        sequence = (
            'name',
            'workflow',
            'action',
            'execute',
            'execute_until',
            'status',
            'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'scheduler-table'}
