# -*- coding: utf-8 -*-

"""Functions to clone the actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from ontask import create_new_name, models
from ontask.condition import services as condition_services
from ontask.core import ajax_required, get_condition, is_instructor


@user_passes_test(is_instructor)
@ajax_required
@require_POST
@get_condition(pf_related='action')
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
    del pk, workflow
    if action_pk:
        action = models.Action.objects.filter(id=action_pk).first()
        if not action:
            messages.error(request, _('Incorrect action id.'))
            return http.JsonResponse({'html_redirect': ''})
    else:
        action = condition.action

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content and action:
        condition.action.set_text_content(action_content)

    condition_services.do_clone_condition(
        request.user,
        condition,
        new_action=action,
        new_name=create_new_name(condition.name, action.conditions))

    messages.success(request, _('Condition successfully cloned.'))

    return http.JsonResponse({'html_redirect': ''})
