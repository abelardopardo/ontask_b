# -*- coding: utf-8 -*-

"""Send Email Messages with the rendered content in the action."""
from collections import OrderedDict
from typing import Dict, List, Optional

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import models, tasks
from ontask.action import forms
from ontask.action.services.email import ActionManagerEmail
from ontask.action.services.manager_factory import action_process_factory
from ontask.celery import get_task_logger

LOGGER = get_task_logger('celery_execution')


class RubricTable(tables.Table):
    """Table to represent the rubric."""

    criterion = tables.Column(verbose_name=_('Criterion'))

    class Meta:
        """Define fields, sequence, attrs, etc."""

        fields = ('criterion',)

        sequence = ('criterion',)

        attrs = {
            'class': 'table table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'rubric-table',
        }


def _verify_criteria_loas(
    criteria: List[models.ActionColumnConditionTuple]
) -> bool:
    """Verify that all columns have all categories identical."""
    if not criteria:
        return True

    loas = set(criteria[0].column.categories)
    return all(
        loas == set(criterion.column.categories)
        for criterion in criteria[1:]
    )


def _create_rubric_table(
    action: models.Action,
    criteria: List[models.ActionColumnConditionTuple],
    context: Dict
):
    if not criteria:
        return

    # Create the extra columns in the table with the categories
    extra_columns = []
    loas = criteria[0].column.categories
    # Get the extra columns for the rubric
    for idx, loa in enumerate(loas):
        extra_columns.append((
            'loa_{0}'.format(idx),
            tables.Column(verbose_name=loa)
        ))

    # Create the table data
    table_data = []
    cell_ctx = {'action_id': action.id}
    for criterion in criteria:
        cell_ctx['column_id'] = criterion.column.id
        rubric_row = OrderedDict([(
            'criterion',
            render_to_string(
                'workflow/includes/partial_criterion_cell.html',
                context={'criterion': criterion, 'action': action}))])

        cels = models.RubricCell.objects.filter(
            action=action,
            column=criterion.column)
        for idx in range(len(loas)):
            cell = cels.filter(loa_position=idx).first()
            loa_str = 'loa_{0}'.format(idx)
            cell_ctx['loa_idx'] = idx
            if cell:
                cell_ctx['description_text'] = cell.description_text
                cell_ctx['feedback_text'] = cell.feedback_text
            else:
                cell_ctx['description_text'] = ''
                cell_ctx['feedback_text'] = ''

            rubric_row[loa_str] = render_to_string(
                'action/includes/partial_rubriccell.html',
                cell_ctx
            )
        table_data.append(rubric_row)

    context['rubric_table'] = RubricTable(
        table_data,
        orderable=False,
        extra_columns=extra_columns)


class ActionManagerRubric(ActionManagerEmail):
    """Class to serve running an email action."""

    def extend_edit_context(
        self,
        workflow: models.Workflow,
        action: models.Action,
        context: Dict,
    ) -> Optional[str]:
        """Get the context dictionary to render the GET request.

        :param workflow: Workflow being used
        :param action: Action being used
        :param context: Initial dictionary to extend
        :return: An error string or None if everything was correct.
        """
        criteria = action.column_condition_pair.all()
        if not _verify_criteria_loas(criteria):
            return _('Inconsistent LOA in rubric criteria')
        _create_rubric_table(action, criteria, context)

        columns_to_insert_qs = action.workflow.columns.exclude(
            column_condition_pair__action=action,
        ).exclude(
            is_key=True,
        ).distinct().order_by('position')
        if criteria:
            columns_to_insert = [
                column
                for column in columns_to_insert_qs
                if set(column.categories) == set(criteria[0].column.categories)
            ]
        else:
            columns_to_insert = [
                column
                for column in columns_to_insert_qs
                if column.categories]
        context['columns_to_insert'] = columns_to_insert

        return None


process_rubric = ActionManagerRubric(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_rubric.html',
    run_form_class=forms.SendListActionRunForm,
    run_template='action/request_send_list_data.html',
    log_event=models.Log.ACTION_RUN_EMAIL)

action_process_factory.register_producer(
    models.Action.RUBRIC_TEXT,
    process_rubric)

tasks.task_execute_factory.register_producer(
    models.Action.RUBRIC_TEXT,
    process_rubric)
