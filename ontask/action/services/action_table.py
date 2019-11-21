# -*- coding: utf-8 -*-

"""Service to produce the table with the action objects."""

import django_tables2 as tables
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ontask import models, simplify_datetime_str
from ontask.core.tables import OperationsColumn


class ActionTable(tables.Table):
    """Class to render the list of actions per workflow.

    The Operations column is taken from another class to centralise the
    customisation.
    """

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(verbose_name=_('Description'))

    action_type = tables.TemplateColumn(
        template_name='action/includes/partial_action_type.html',
        verbose_name=_('Type'))

    last_executed_log = tables.LinkColumn(
        verbose_name=_('Last executed'),
        empty_values=['', None],
        viewname='logs:view',
        text=lambda record: simplify_datetime_str(
            record.last_executed_log.modified),
        kwargs={'pk': tables.A('last_executed_log.id')},
        attrs={'a': {'class': 'spin'}},
    )

    #
    # Operatiosn available per action type (see partial_action_operations.html)
    #
    #  Action type               |  Email  |  ZIP |  URL  |  RUN  |
    #  ------------------------------------------------------------
    #  Personalized text         |    X    |   X  |   X   |   X   |
    #  Personalized canvas email |    X    |      |       |   X   |
    #  Personalized JSON         |         |      |   ?   |   X   |
    #  Survey                    |         |      |   X   |   X   |
    #  Todo List                 |         |      |   X   |   X   |
    #
    operations = OperationsColumn(
        verbose_name='',
        template_file='action/includes/partial_action_operations.html',
        template_context=lambda record: {
            'id': record.id,
            'action_tval': record.action_type,
            'is_out': int(record.is_out),
            'is_executable': record.is_executable,
            'serve_enabled': record.serve_enabled},
    )

    def render_name(self, record):
        """Render name as a link with a potential flag."""
        return render_to_string(
            'action/includes/partial_action_name.html',
            context={
                'action_id': record.id,
                'danger_msg': (
                    record.get_row_all_false_count or not record.is_executable
                ),
                'action_name': record.name,
            },
        )

    class Meta(object):
        """Define model, fields and ordering."""

        model = models.Action
        fields = (
            'name',
            'description_text',
            'action_type',
            'last_executed_log',
        )
        sequence = (
            'action_type',
            'name',
            'description_text',
            'last_executed_log',
        )
        exclude = ('content', 'serve_enabled', 'filter')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'action-table',
        }
