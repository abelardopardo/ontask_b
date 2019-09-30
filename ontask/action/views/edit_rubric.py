# -*- coding: utf-8 -*-

"""View to edit rubric actions."""

from collections import OrderedDict
from typing import Dict, List, Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask.action.forms import (
    EditActionOutForm, FilterForm, RubricCellForm, RubricLOAForm)
from ontask.action.views.edit_personalized import text_renders_correctly
from ontask.core.decorators import ajax_required, get_action
from ontask.core.permissions import is_instructor
from ontask.models import (
    Action, ActionColumnConditionTuple, Log, RubricCell, Workflow,
)


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


def _verify_criteria_loas(criteria: List[ActionColumnConditionTuple]) -> bool:
    """Verify that all columns have all categories identical."""
    if not criteria:
        return True

    loas = set(criteria[0].column.categories)
    return all(
        loas == set(criterion.column.categories)
        for criterion in criteria[1:]
    )


def _create_rubric_table(
    request: HttpRequest,
    action: Action,
    criteria: List[ActionColumnConditionTuple],
    context: Dict
):
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
                context={'criterion': criterion, 'action': action},
                request=request))])

        cels = RubricCell.objects.filter(
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


def edit_action_rubric(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Edit action out.

    :param request: Request object
    :param workflow: The workflow with the action
    :param action: Action
    :return: HTML response
    """
    # Create the form
    form = EditActionOutForm(request.POST or None, instance=action)

    form_filter = FilterForm(
        request.POST or None,
        instance=action.get_filter(),
        action=action
    )

    # Processing the request after receiving the text from the editor
    if request.method == 'POST' and form.is_valid() and form_filter.is_valid():
        # Get content
        text_content = form.cleaned_data.get('text_content')

        # Render the content as a template and catch potential problems.
        if text_renders_correctly(text_content, action, form):
            # Log the event
            action.log(request.user, Log.ACTION_UPDATE)

            # Text is good. Update the content of the action
            action.set_text_content(text_content)
            action.save()

            if request.POST['Submit'] == 'Submit':
                return redirect(request.get_full_path())

            return redirect('action:index')

    # Get the filter or None
    filter_condition = action.get_filter()

    criteria = action.column_condition_pair.all()

    if not _verify_criteria_loas(criteria):
        messages.error(
            request,
            _('Inconsistent LOA in rubric criteria')
        )
        return redirect(reverse('action:index'))

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

    # This is a GET request or a faulty POST request
    context = {
        'form': form,
        'form_filter': form_filter,
        'filter_condition': filter_condition,
        'action': action,
        'load_summernote': Action.LOAD_SUMMERNOTE[action.action_type],
        'query_builder_ops': action.workflow.get_query_builder_ops_as_str(),
        'attribute_names': [
            attr for attr in list(action.workflow.attributes.keys())
        ],
        'columns': action.workflow.columns.all(),
        'selected_rows':
            filter_condition.n_rows_selected
            if filter_condition else -1,
        'has_data': action.workflow.has_table(),
        'is_send_list': (
            action.action_type == Action.SEND_LIST
            or action.action_type == Action.SEND_LIST_JSON),
        'is_personalized_text': action.action_type == Action.PERSONALIZED_TEXT,
        'is_rubric_cell': action.action_type == Action.RUBRIC_TEXT,
        'rows_all_false': action.get_row_all_false_count(),
        'total_rows': action.workflow.nrows,
        'all_false_conditions': False,
        'columns_to_insert': columns_to_insert}

    # Get additional context to render the page depending on the action type
    if criteria:
        _create_rubric_table(request, action, criteria, context)

    # Return the same form in the same page
    return render(request, 'action/edit_rubric.html', context=context)


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def edit_rubric_cell(
    request: HttpRequest,
    pk: int,
    cid: int,
    loa_pos: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Edit a cell in a rubric.

    :param request:

    :param pk: Action ID

    :param cid: Column id

    :param loa_pos: Level of attainment position in the column categories

    :return: JSON Response
    """
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    form = RubricCellForm(
        request.POST or None,
        instance=action.rubric_cells.filter(
            column=cid,
            loa_position=loa_pos).first())

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        cell = form.save(commit=False)
        if cell.id is None:
            # New cell in the rubric
            cell.action = action
            cell.column = action.workflow.columns.get(pk=cid)
            cell.loa_position = loa_pos
        cell.save()
        cell.log(request.user, Log.ACTION_RUBRIC_CELL_EDIT)
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_rubriccell_edit.html',
            {'form': form,
             'pk': pk,
             'cid': cid,
             'loa_pos': loa_pos},
            request=request)})

@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def edit_rubric_loas(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Edit a cell in a rubric.

    :param request:

    :param pk: Action ID

    :return: JSON Response
    """
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    form = RubricLOAForm(
        request.POST or None,
        criteria=[acc.column for acc in action.column_condition_pair.all()])

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        loas = [
            loa.strip()
            for loa in form.cleaned_data['levels_of_attainment'].split(',')]

        # Update all columns
        try:
            with transaction.atomic():
                for acc in action.column_condition_pair.all():
                    acc.column.set_categories(loas, True)
                    acc.column.save()
        except Exception as exc:
            messages.error(
                request,
                _('Incorrect level of attainment values ({0}).').format(
                    str(exc)))

        # Log the event
        action.log(request.user, Log.ACTION_RUBRIC_LOA_EDIT, new_loas=loas)

        # Done processing the correct POST request
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_rubric_loas_edit.html',
            {'form': form, 'pk': pk},
            request=request)})
