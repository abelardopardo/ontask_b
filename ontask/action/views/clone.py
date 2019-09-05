# -*- coding: utf-8 -*-

"""Functions to clone the actions."""

import copy
from builtins import str
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import create_new_name
from ontask.core.decorators import ajax_required, get_action, get_condition
from ontask.core.permissions import is_instructor
from ontask.dataops.formula import get_variables
from ontask.models import (
    Action, ActionColumnConditionTuple, Condition, Log, Workflow,
)


def do_clone_condition(
    condition: Condition,
    new_action: Action = None,
    new_name: str = None,
) -> Condition:
    """Clone a condition.

    Function to clone a condition and change action and/or name

    :param condition: Condition to clone

    :param new_action: New action to point

    :param new_name: New name

    :return: New condition
    """
    if new_name is None:
        new_name = condition.name
    if new_action is None:
        new_action = condition.action

    new_condition = Condition(
        name=new_name,
        description_text=condition.description_text,
        action=new_action,
        formula=copy.deepcopy(condition.formula),
        n_rows_selected=condition.n_rows_selected,
        is_filter=condition.is_filter
    )
    new_condition.save()

    try:
        # Update the many to many field.
        new_condition.columns.set(new_condition.action.workflow.columns.filter(
            name__in=get_variables(new_condition.formula),
        ))
    except Exception as exc:
        new_condition.delete()
        raise exc

    return new_condition


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
    if new_name is None:
        new_name = action.name
    if new_workflow is None:
        new_workflow = action.workflow

    new_action = Action(
        name=new_name,
        description_text=action.description_text,
        workflow=new_workflow,
        last_executed_log=None,
        action_type=action.action_type,
        serve_enabled=action.serve_enabled,
        active_from=action.active_from,
        active_to=action.active_to,
        rows_all_false=copy.deepcopy(action.rows_all_false),
        text_content=action.text_content,
        target_url=action.target_url,
        shuffle=action.shuffle,
    )
    new_action.save()

    try:
        # Clone the column/condition pairs field.
        for acc_tuple in action.column_condition_pair.all():
            cname = acc_tuple.condition.name if acc_tuple.condition else None
            ActionColumnConditionTuple.objects.get_or_create(
                action=new_action,
                column=new_action.workflow.columns.get(
                    name=acc_tuple.column.name),
                condition=new_action.conditions.filter(name=cname).first(),
            )

        # Clone the conditions
        for condition in action.conditions.all():
            do_clone_condition(condition, new_action)

        # Update
        new_action.save()
    except Exception as exc:
        new_action.delete()
        raise exc

    return new_action


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def clone_action(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """View to clone an action.

    :param request: Request object
    :param pk: id of the action to clone
    :return:
    """
    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'action/includes/partial_action_clone.html',
                {'pk': pk, 'name': action.name},
                request=request),
        })

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

    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_condition(pf_related='actions', is_filter=None)
def clone_condition(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    condition: Optional[Condition] = None,
    action_pk: Optional[int] = None,
) -> JsonResponse:
    """JSON request to clone a condition.

    The post request must come with the action_content

    :param request: Request object
    :param pk: id of the condition to clone
    :param action_pk: Primary key of the action to receive the condition
    :return: JSON response
    """
    if action_pk:
        action = Action.objects.filter(id=action_pk).first()
        if not action:
            messages.error(request, _('Incorrect action id.'))
            return JsonResponse({'html_redirect': ''})
    else:
        action = condition.action

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
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
