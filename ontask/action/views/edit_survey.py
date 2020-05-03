# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ontask import models
from ontask.action import forms
from ontask.core import (
    ajax_required, get_action, get_columncondition, get_workflow,
    is_instructor,
)


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_POST
@get_action(pf_related=['columns', 'actions'])
def select_column_action(
    request: http.HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
    key: Optional[bool] = None,
) -> http.JsonResponse:
    """Operation to add a column to a survey.

    :param request: Request object
    :param pk: Action PK
    :param cpk: column PK.
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being edited (set by the decorators)
    :param key: The columns is a key column
    :return: JSON response
    """
    del pk
    if cpk == -1:
        # Unsetting key column
        action.column_condition_pair.filter(column__is_key=True).delete()
        return http.JsonResponse({'html_redirect': ''})

    # Get the column
    column = workflow.columns.filter(pk=cpk).first()
    if not column:
        return http.JsonResponse({'html_redirect': reverse('action:index')})

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
    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@get_action(pf_related=['actions', 'columns'])
def unselect_column_action(
    request: http.HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.HttpResponse:
    """Unselect a column from action in.

    :param request: Request object
    :param pk: Action PK
    :param cpk: column PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being edited (set by the decorators)
    :return: JSON response
    """
    del request, pk
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
@require_POST
@get_columncondition(pf_related=['columns', 'actions'])
def select_condition_for_question(
    request: http.HttpRequest,
    pk: int,
    condpk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    cc_tuple: Optional[models.ActionColumnConditionTuple] = None,
) -> http.JsonResponse:
    """Select condition for a question in a survey.

    :param request: Request object
    :param pk: tuple ActionColumnCondition PK
    :param condpk: Condition PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param cc_tuple: ActionColumnCondition object being edited (set by the
    decorators)
    :return: JSON response
    """
    del request, pk, workflow
    condition = None
    if condpk:
        # Get the condition
        condition = cc_tuple.action.conditions.filter(pk=condpk).first()
        if not condition:
            return http.JsonResponse(
                {'html_redirect': reverse('action:index')})

    # Assign the condition to the tuple and save
    cc_tuple.condition = condition
    cc_tuple.save(update_fields=['condition'])

    # Refresh the page to show the column in the list.
    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def shuffle_questions(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Enable/Disable the shuffle question flag a survey.

    :param request: Request object
    :param pk: Action PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being manipulated (set by the decorators)
    :return: HTML response
    """
    del request, pk, workflow
    action.shuffle = not action.shuffle
    action.save(update_fields=['shuffle'])

    return http.JsonResponse({'is_checked': action.shuffle})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
@get_columncondition()
def toggle_question_change(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    cc_tuple: Optional[models.ActionColumnConditionTuple] = None,
) -> http.JsonResponse:
    """Enable/Disable changes in the question.

    :param request: Request object
    :param pk: Action/Question/Condition PK
    :param workflow: Workflow being manipulated (set by the decorators)
    :param cc_tuple: Action/Column/Condition tuple being manipulated (set by
    the decorator)
    :return: HTML response
    """
    del pk, workflow
    cc_tuple.changes_allowed = not cc_tuple.changes_allowed
    cc_tuple.save(update_fields=['changes_allowed'])
    cc_tuple.log(request.user, models.Log.ACTION_QUESTION_TOGGLE_CHANGES)

    return http.JsonResponse({'is_checked': cc_tuple.changes_allowed})


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def edit_description(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Edit the description attached to an action.

    :param request: AJAX request
    :param pk: Action ID
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being modified (set by the decorators)
    :return: AJAX response
    """
    del pk, workflow
    # Create the form
    form = forms.ActionDescriptionForm(
        request.POST or None,
        instance=action)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        action.save(update_fields=['name', 'description_text'])

        action.log(request.user, 'update')

        # Request is correct
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_edit_description.html',
            {'form': form, 'action': action},
            request=request),
    })
