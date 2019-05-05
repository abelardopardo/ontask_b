# -*- coding: utf-8 -*-

"""Functions to clone the actions."""

from builtins import str
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from action.models import Action, ActionColumnConditionTuple, Condition
from logs.models import Log
from ontask import create_new_name
from ontask.permissions import is_instructor
from workflow.models import Workflow
from ontask.decorators import get_workflow


def do_clone_condition(
    condition: Condition,
    new_action: Action = None,
    new_name: str = None,
):
    """Clone a condition.

    Function to clone a condition and change action and/or name
    :param condition: Condition to clone
    :param new_action: New action to point
    :param new_name: New name
    :return: New condition
    """
    condition.id = None
    if new_action:
        condition.action = new_action
    if new_name:
        condition.name = new_name
    condition.save()

    return condition


def do_clone_action(
    action: Action,
    new_workflow: Workflow = None,
    new_name: str = None,
):
    """Clone an action.

    Function that given an action clones it and changes workflow and name
    :param action: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """
    # Store the old object id before squashing it
    old_id = action.id

    # Clone
    action.id = None

    # Update some of the fields
    if new_name:
        action.name = new_name
    if new_workflow:
        action.workflow = new_workflow

    # Update
    action.save()

    # Get back the old action
    old_action = Action.objects.prefetch_related(
        'column_condition_pair', 'conditions',
    ).get(id=old_id)

    # Clone the columns field (in case of an action in).
    if action.is_in:
        action.column_condition_pair.delete()
        for acc_tuple in old_action.column_condition_pair.all():
            __, __ = ActionColumnConditionTuple.objects.get_or_create(
                action=action,
                column=acc_tuple.column,
                condition=acc_tuple.condition,
            )

    # Clone the conditions
    for condition in old_action.conditions.all():
        do_clone_condition(condition, action)

    # Update
    action.save()

    return action


@user_passes_test(is_instructor)
def clone_action(request: HttpRequest, pk: int) -> JsonResponse:
    """View to clone an action.

    :param request: Request object
    :param pk: id of the action to clone
    :return:
    """
    # JSON response
    resp_data = {}

    # Get the current workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        resp_data['html_redirect'] = reverse('home')
        return JsonResponse(resp_data)

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        resp_data['html_redirect'] = reverse('action:index')
        return JsonResponse(resp_data)

    if request.method == 'GET':
        resp_data['html_form'] = render_to_string(
            'action/includes/partial_action_clone.html',
            {'pk': pk, 'name': action.name},
            request=request)
        return JsonResponse(resp_data)

    # POST REQUEST!

    log_payload = {
        'id_old': action.id,
        'name_old': action.name,
    }

    action = do_clone_action(
        action,
        new_workflow=None,
        new_name=create_new_name(action.name, workflow.actions))

    # Log event
    log_payload['id_new'] = action.id
    log_payload['name_new'] = action.name
    Log.objects.register(
        request.user,
        Log.ACTION_CLONE,
        workflow,
        log_payload,
    )

    messages.success(request, _('Action successfully cloned.'))

    resp_data['html_redirect'] = reverse('action:index')
    return redirect(reverse('action:index'))


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def clone_condition(
    request: HttpRequest,
    pk: int,
    action_pk: Optional[int] = None,
) -> JsonResponse:
    """JSON request to clone a condition.

    The post request must come with the action_content

    :param request: Request object
    :param pk: id of the condition to clone
    :param action_pk: Primary key of the action to receive the condition
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return JsonResponse({'html_redirect': reverse('home')})

    # Get the condition
    condition = Condition.objects.filter(pk=pk).filter(
        Q(action__workflow__user=request.user)
        | Q(action__workflow__shared=request.user),
        is_filter=False,
        action__workflow=workflow,
    ).select_related('action').first()

    if not condition:
        messages.error(
            request,
            _('Condition cannot be cloned.'))
        return JsonResponse({'html_redirect': reverse('action:index')})

    action = condition.action
    if action_pk:
        action = workflow.actions.filter(pk=action_pk).first()
        if not action:
            # The given action is not attached to the workflow
            return JsonResponse({'html_redirect': reverse('home')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content', None)
    if action_content:
        condition.action.set_text_content(action_content)
        condition.action.save()

    log_context = {
        'id_old': condition.id,
        'name_old': condition.name}

    condition = do_clone_condition(
        condition,
        new_action=action,
        new_name=create_new_name(condition.name, action.conditions))

    # Log event
    log_context['id_new'] = condition.id
    log_context['name_new'] = condition.name
    Log.objects.register(
        request.user,
        Log.CONDITION_CLONE,
        condition.action.workflow,
        log_context)

    messages.success(request, _('Condition successfully cloned.'))

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})
