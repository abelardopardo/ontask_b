# -*- coding: utf-8 -*-

"""Functions to clone the actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ontask import create_new_name, models
from ontask.action import services
from ontask.core import ajax_required, get_action, is_instructor


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
