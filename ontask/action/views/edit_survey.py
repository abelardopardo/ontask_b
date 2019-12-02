# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import models
from ontask.action.forms import ActionDescriptionForm
from ontask.core.decorators import (
    ajax_required, get_action,
    get_columncondition, get_workflow,
)
from ontask.core.permissions import is_instructor


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_action(pf_related=['columns', 'actions'])
def select_column_action(
    request: HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
    key: Optional[bool] = None,
) -> JsonResponse:
    """Operation to add a column to a survey.

    :param request: Request object
    :param pk: Action PK
    :param cpk: column PK.
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being edited (set by the decorators)
    :param key: The columns is a key column
    :return: JSON response
    """
    if cpk == -1:
        # Unsetting key column
        action.column_condition_pair.filter(column__is_key=True).delete()
        return JsonResponse({'html_redirect': ''})

    # Get the column
    column = workflow.columns.filter(pk=cpk).first()
    if not column:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Parameters are correct, so add the column to the action.
    if key:
        # There can only be one key column in these pairs
        action.column_condition_pair.filter(column__is_key=True).delete()

    if key != 0:
        # Insert the column in the pairs
        acc, __ = models.ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=column,
            condition=None)

        acc.log(request.user, models.Log.ACTION_QUESTION_ADD)

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@get_action(pf_related=['actions', 'columns'])
def unselect_column_action(
    request: HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> HttpResponse:
    """Unselect a column from action in.

    :param request: Request object
    :param pk: Action PK
    :param cpk: column PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being edited (set by the decorators)
    :return: JSON response
    """
    # Get the column
    column = workflow.columns.filter(pk=cpk).first()
    if not column:
        return redirect(reverse('action:index'))

    # Parameters are correct, so remove the column from the action.
    action.column_condition_pair.filter(column=column).delete()

    return redirect(reverse('action:edit', kwargs={'pk': action.id}))


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_columncondition(pf_related=['columns', 'actions'])
def select_condition_for_question(
    request: HttpRequest,
    pk: int,
    condpk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    cc_tuple: Optional[models.ActionColumnConditionTuple] = None,
) -> JsonResponse:
    """Select condition for a question in a survey.

    :param request: Request object
    :param pk: tuple ActionColumnCondition PK
    :param condpk: Condition PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param cc_tuple: ActionColumnCondition object being edited (set by the
    decorators)
    :return: JSON response
    """
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
@ajax_required
@get_action(pf_related='actions')
def shuffle_questions(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> JsonResponse:
    """Enable/Disable the shuffle question flag a survey.

    :param request: Request object
    :param pk: Action PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being manipulated (set by the decorators)
    :return: HTML response
    """
    # Check if the workflow is locked
    action.shuffle = not action.shuffle
    action.save()

    return JsonResponse({'is_checked': action.shuffle})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
@get_columncondition()
def toggle_question_change(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    cc_tuple: Optional[models.ActionColumnConditionTuple] = None,
) -> JsonResponse:
    """Enable/Disable changes in the question.

    :param request: Request object
    :param pk: Action/Question/Condition PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param cc_tuple: Action/Column/Condition tuple being manipulated (set by
    the decorator)
    :return: HTML response
    """
    cc_tuple.changes_allowed = not cc_tuple.changes_allowed
    cc_tuple.save()
    cc_tuple.log(request.user, models.Log.ACTION_QUESTION_TOGGLE_CHANGES)

    return JsonResponse({'is_checked': cc_tuple.changes_allowed})


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def edit_description(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> JsonResponse:
    """Edit the description attached to an action.

    :param request: AJAX request
    :param pk: Action ID
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being modified (set by the decorators)
    :return: AJAX response
    """
    # Create the form
    form = ActionDescriptionForm(
        request.POST or None,
        instance=action)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        action.save()

        action.log(request.user, 'update')

        # Request is correct
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_edit_description.html',
            {'form': form, 'action': action},
            request=request),
    })
