# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask.action.forms import ActionDescriptionForm
from ontask.core.decorators import (
    ajax_required, get_action, get_columncondition, get_workflow,
)
from ontask.core.permissions import is_instructor
from ontask.models import (
    Action, ActionColumnConditionTuple, Log, Workflow,
)


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_action(pf_related=['columns', 'actions'])
def select_column_action(
    request: HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
    key: Optional[bool] = None,
) -> JsonResponse:
    """Operation to add a column to a survey.

    :param request: Request object

    :param pk: Action PK

    :param cpk: column PK.

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
        acc = ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=column,
            condition=None)

        acc.log(request.user, Log.ACTION_QUESTION_ADD)

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@get_action(pf_related=['actions', 'columns'])
def unselect_column_action(
    request: HttpRequest,
    pk: int,
    cpk: Optional[int] = -1,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Unselect a column from action in.

    :param request: Request object
    :param apk: Action PK
    :param cpk: column PK
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
    workflow: Optional[Workflow] = None,
    cc_tuple: Optional[ActionColumnConditionTuple] = None,
) -> JsonResponse:
    """Select condition for a question in a survey.

    :param request: Request object

    :param tpk: tuple ActionColumnCondition PK

    :param condpk: Condition PK

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
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Enable/Disable the shuffle question flag in Surveys.

    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """
    # Check if the workflow is locked
    action.shuffle = not action.shuffle
    action.save()

    return JsonResponse({'is_checked': action.shuffle})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
def toggle_question_change(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Enable/Disable changes in the question.

    :param request: Request object
    :param pk: Action/Question/Condition PK
    :return: HTML response
    """
    # Check if the workflow is locked
    acc_item = ActionColumnConditionTuple.objects.filter(pk=pk).first()
    if not acc_item:
        messages.error(
            request,
            _('Incorrect invocation of toggle question change function.'))
        return JsonResponse({}, status=404)

    if acc_item.action.workflow != workflow:
        messages.error(
            request,
            _('Incorrect invocation of toggle question change function.'))
        return JsonResponse({}, status=404)

    acc_item.changes_allowed = not acc_item.changes_allowed
    acc_item.save()
    acc_item.log(request.user, Log.ACTION_QUESTION_TOGGLE_CHANGES)

    return JsonResponse({'is_checked': acc_item.changes_allowed})


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def edit_description(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Edit the description attached to an action.

    :param request: AJAX request

    :param pk: Action ID

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
