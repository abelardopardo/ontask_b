# -*- coding: utf-8 -*-

"""View to edit rubric actions."""

from collections import OrderedDict
from typing import Dict, List

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask.action.forms import EditActionOutForm, FilterForm
from ontask.action.views.edit_personalized import text_renders_correctly
from ontask.models import Action, Column, Log, RubricCell, Workflow

EDIT_CELL_LINK = """<a class="btn btn-sm btn-light" href="{% url 'workflow:criterion_edit' criterion.id column.id %}"
     title="{% trans 'Edit this cell' %}">
    <span class="fa fa-pencil"></span></a>"""

class RubricTable(tables.Table):
    """Table to represent the rubric."""

    criterion = tables.Column(verbose_name=_('Criterion'))

    def __init__(self, *args, **kwargs):
        """Store the levels of attainment"""
        super().__init__(*args, **kwargs)

    class Meta:
        """Define fields, sequence, attrs, etc."""

        fields = ('criterion', 'loa_0', 'loa_1')

        sequence = ('criterion', 'loa_0', 'loa_1')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'rubric-table',
        }


def _verify_criteria_loas(criteria: List[Column]) -> bool:
    """Verify that all columns have all categories identical."""
    if not criteria:
        return True

    loas = set(criteria[0].categories)
    if any(loas != set(criterion.categories) for criterion in criteria[1:]):
        return False
    return True


def _update_rubric_context(
    request: HttpRequest,
    action: Action,
    criteria: List[Column],
    context: Dict
):
    # Create the rubric table
    extra_columns = []

    loas = criteria[0].categories
    # Get the extra columns for the rubric
    for idx, loa in enumerate(loas):
        extra_columns.append((
            'loa_{0}'.format(idx),
            tables.Column(verbose_name=loa)
        ))

    # Create the table
    table_data = []
    for criterion in criteria:
        rubric_row = OrderedDict(
            [('criterion', criterion.name)]
            + [(loa, ('', '')) for loa in loas]
        )

        rubric_row['criterion'] = render_to_string(
            'workflow/includes/partial_criterion_cell.html',
            context={'criterion': criterion, 'action': action},
            request=request)

        cels = RubricCell.objects.filter(action=action, column=criterion)
        for cel in cels:
            rubric_row[cel.category] = (
                cel.descriptino_text,
                cel.feedback_text)
        table_data.append(rubric_row)

    context['rubric_table'] = RubricTable(
        table_data,
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
            Log.objects.register(
                request.user,
                Log.ACTION_UPDATE,
                action.workflow,
                {'id': action.id,
                 'name': action.name,
                 'workflow_id': workflow.id,
                 'workflow_name': workflow.name,
                 'content': text_content})

            # Text is good. Update the content of the action
            action.set_text_content(text_content)
            action.save()

            if request.POST['Submit'] == 'Submit':
                return redirect(request.get_full_path())

            return redirect('action:index')

    # Get the filter or None
    filter_condition = action.get_filter()

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
        'columns_to_insert': action.workflow.columns.exclude(
            column_condition_pair__action=action,
        ).exclude(
            is_key=True,
        ).exclude(
            categories=[]
        ).distinct().order_by('position'),
    }

    criteria = [
        ccp.column
        for ccp in action.column_condition_pair.all()
        if ccp.action == action]

    if not _verify_criteria_loas(criteria):
        messages.error(
            request,
            _('Inconsistent LOA in rubric criteria')
        )
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Get additional context to render the page depending on the action type
    if criteria:
        _update_rubric_context(request, action, criteria, context)

    # Return the same form in the same page
    return render(request, 'action/edit_rubric.html', context=context)
