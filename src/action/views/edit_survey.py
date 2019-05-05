# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""

from typing import Optional

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from action.forms import ActionDescriptionForm
from action.models import Action, ActionColumnConditionTuple
from logs.models import Log
from ontask.decorators import get_workflow
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from visualizations.plotly import PlotlyHandler
from workflow.models import Workflow


class ColumnSelectedTable(tables.Table):
    """Table to render the columns selected for a given action in."""

    column__name = tables.Column(verbose_name=_('Name'))  # noqa: Z116
    column__description_text = tables.Column(  # noqa: Z116
        verbose_name=_('Description (shown to learners)'),
        default='',
    )
    condition = tables.Column(  # noqa: Z116
        verbose_name=_('Condition'),
        empty_values=[-1],
    )

    # Template to render the extra column created dynamically
    ops_template = 'action/includes/partial_column_selected_operations.html'

    def __init__(self, *args, **kwargs):
        """Store the condition list."""
        self.condition_list = kwargs.pop('condition_list')
        super().__init__(*args, **kwargs)

    def render_column__name(self, record):  # noqa: Z116
        """Render as a link."""
        return format_html(
            '<a href="#" data-toggle="tooltip"'
            + ' class="js-workflow-question-edit" data-url="{0}"'
            + ' title="{1}">{2}</a>',
            reverse(
                'workflow:question_edit',
                kwargs={'pk': record['column__id']}),
            _('Edit the question'),
            record['column__name'],
        )

    def render_condition(self, record):
        """Render with template to select condition."""
        return render_to_string(
            'action/includes/partial_column_selected_condition.html',
            {
                'id': record['id'],
                'cond_selected': record['condition__name'],
                'conditions': self.condition_list,
            },
        )

    class Meta(object):
        """Define fields, sequence, attrs and row attrs."""

        fields = (
            'column__id',
            'column__name',
            'column__description_text',
            'condition',
            'operations')

        sequence = (
            'column__name',
            'column__description_text',
            'condition',
            'operations')

        attrs = {
            'class': 'table table-hover table-bordered',
            'style': 'width: 100%;',
            'id': 'column-selected-table',
        }

        row_attrs = {
            'class': lambda record: 'danger' if not record[
                'column__description_text'
            ] else '',
        }


def edit_action_in(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Edit an action in.

    :param request: Request object
    :param workflow: workflow
    :param action: Action
    :return: HTTP response
    """
    # All tuples (action, column, condition) to consider
    tuples = action.column_condition_pair.all()

    # Columns
    all_columns = workflow.columns.all()

    # Conditions
    filter_condition = action.get_filter()
    all_conditions = action.conditions.filter(is_filter=False)

    # Create the context info.
    context = {
        'action': action,
        # Workflow elements
        'total_rows': workflow.nrows,
        'query_builder_ops': workflow.get_query_builder_ops_as_str(),
        'has_data': workflow.has_table(),
        'selected_rows':
            filter_condition.n_rows_selected if filter_condition else -1,
        'all_false_conditions': any(
            cond.n_rows_selected == 0 for cond in all_conditions
        ),
        # Column elements
        'key_columns': all_columns.filter(is_key=True),
        'key_selected': tuples.filter(column__is_key=True).first(),
        'has_no_key': tuples.filter(column__is_key=False).exists(),
        'any_empty_description': tuples.filter(
            column__description_text='',
            column__is_key=False,
        ).exists(),
        'columns_to_insert': all_columns.exclude(
            column_condition_pair__action=action,
        ).exclude(
            is_key=True,
        ).distinct().order_by('position'),
        'column_selected_table': ColumnSelectedTable(
            tuples.filter(column__is_key=False).values(
                'id',
                'column__id',
                'column__name',
                'column__description_text',
                'condition__name',
            ),
            orderable=False,
            extra_columns=[(
                'operations',
                OperationsColumn(
                    verbose_name='',
                    template_file=ColumnSelectedTable.ops_template,
                    template_context=lambda record: {
                        'id': record['column__id'],
                        'aid': action.id}),
            )],
            condition_list=all_conditions,
        ),
        # Conditions
        'filter_condition': filter_condition,
        'conditions': all_conditions,
        'vis_scripts': PlotlyHandler.get_engine_scripts(),
    }

    return render(request, 'action/edit_in.html', context)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def select_column_action(
    request: HttpRequest,
    apk: int,
    cpk: int,
    key: Optional[bool] = None,
) -> JsonResponse:
    """Operation to add a column to action in.

    :param request: Request object
    :param apk: Action PK
    :param cpk: column PK
    :param key: The columns is a key column
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request, prefetch_related=['columns', 'actions'])
    if not workflow:
        return JsonResponse({'html_redirect': reverse('home')})

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'))
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Get the action and the columns
    action = workflow.actions.filter(
        pk=apk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Get the column
    column = workflow.columns.filter(pk=cpk).first()
    if not column:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Parameters are correct, so add the column to the action.
    if key:
        # There can only be one key column in these pairs
        action.column_condition_pair.filter(column__is_key=True).delete()

    # Insert the column in the pairs
    ActionColumnConditionTuple.objects.get_or_create(
        action=action,
        column=column,
        condition=None)

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
def unselect_column_action(
    request: HttpRequest,
    apk: int,
    cpk: int,
) -> HttpResponse:
    """Unselect a column from action in.

    :param request: Request object
    :param apk: Action PK
    :param cpk: column PK
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request, prefetch_related=['actions', 'columns'])
    if not workflow:
        return reverse('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    action = workflow.actions.filter(
        pk=apk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect(reverse('action:index'))

    # Get the column
    column = workflow.columns.filter(pk=cpk).first()
    if not column:
        return redirect(reverse('action:index'))

    # Parameters are correct, so remove the column from the action.
    action.column_condition_pair.filter(column=column).delete()

    return redirect(reverse('action:edit', kwargs={'pk': action.id}))


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def select_condition(
    request: HttpRequest,
    tpk: int,
    condpk: Optional[int] = None,
) -> JsonResponse:
    """Select condition for action in.

    :param request: Request object
    :param tpk: tuple ActionColumnCondition PK
    :param condpk: Condition PK
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request, prefetch_related=['columns', 'actions'])
    if not workflow:
        return JsonResponse({'html_redirect': reverse('home')})

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'))
        return JsonResponse({'html_redirect': reverse('action:index')})

    cc_tuple = ActionColumnConditionTuple.objects.filter(pk=tpk).first()
    if not cc_tuple:
        return JsonResponse({'html_redirect': reverse('action:index')})

    condition = None
    if condpk:
        # Get the condition
        condition = cc_tuple.action.conditions.filter(pk=condpk).first()
        if not condition:
            return JsonResponse({'html_redirect': reverse('action:index')})

    # Assign the condition to the tuple and save
    cc_tuple.condition = condition
    cc_tuple.save()

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
def shuffle_questions(request: HttpRequest, pk: int) -> HttpResponse:
    """Enable/Disable the shuffle question flag in Surveys.

    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return reverse('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect(reverse('action:index'))

    action.shuffle = not action.shuffle
    action.save()

    return JsonResponse({'shuffle': action.shuffle})


@user_passes_test(is_instructor)
def edit_description(request: HttpRequest, pk: int) -> JsonResponse:
    """Edit the description attached to an action.

    :param request: AJAX request
    :param pk: Action ID
    :return: AJAX response
    """
    # Try to get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return JsonResponse({'html_redirect': reverse('home')})

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Create the form
    form = ActionDescriptionForm(
        request.POST or None,
        instance=action)

    if request.method == 'GET' or not form.is_valid():
        return JsonResponse({
            'html_form': render_to_string(
                'action/includes/partial_action_edit_description.html',
                {'form': form, 'action': action},
                request=request)
        })

    # Process the POST
    # Save item in the DB
    action.save()

    # Log the event
    Log.objects.register(
        request.user,
        Log.ACTION_UPDATE,
        action.workflow,
        {'id': action.id,
         'name': action.name,
         'workflow_id': workflow.id,
         'workflow_name': workflow.name})

    # Request is correct
    return JsonResponse({'html_redirect': ''})
