# -*- coding: utf-8 -*-

"""Functions to clone the actions."""

from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import create_new_name, models
from ontask.action import services
from ontask.core.decorators import ajax_required, get_action, get_condition
from ontask.core.permissions import is_instructor


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def clone_action(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """View to clone an action.

    :param request: Request object
    :param pk: id of the action to clone
    :param workflow: Workflow being manipulated (set by decorator)
    :param action: Action being cloned (set by decorator)
    :return:
    """
    if request.method == 'GET':
        return http.JsonResponse({
            'html_form': render_to_string(
                'action/includes/partial_action_clone.html',
                {'pk': pk, 'name': action.name},
                request=request),
        })

    services.do_clone_action(
        request.user,
        action,
        new_workflow=None,
        new_name=create_new_name(action.name, workflow.actions))

    messages.success(request, _('Action successfully cloned.'))

    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_condition(pf_related='actions', is_filter=None)
def clone_condition(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
    action_pk: Optional[int] = None,
) -> http.JsonResponse:
    """JSON request to clone a condition.

    The post request must come with the action_content

    :param request: Request object
    :param pk: id of the condition to clone
    :param workflow: Workflow being manipulated (set by decorator)
    :param condition: Condition being cloned (set by decorator)
    :param action_pk: Primary key of the action to receive the condition
    :return: JSON response
    """
    if action_pk:
        action = models.Action.objects.filter(id=action_pk).first()
        if not action:
            messages.error(request, _('Incorrect action id.'))
            return http.JsonResponse({'html_redirect': ''})
    else:
        action = condition.action

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        condition.action.set_text_content(action_content)
        condition.action.save()

    condition = services.do_clone_condition(
        request.user,
        condition,
        new_action=action,
        new_name=create_new_name(condition.name, action.conditions))

    messages.success(request, _('Condition successfully cloned.'))

    return http.JsonResponse({'html_redirect': ''})
