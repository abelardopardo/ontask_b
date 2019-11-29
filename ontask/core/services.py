# -*- coding: utf-8 -*-

"""Wrappers around asynchronous task executions."""
from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext

from ontask import models


def get_execution_items(
    user_id: int,
    workflow_id: Optional[int] = None,
    action_id: Optional[int] = None,
) -> Tuple:
    """Get the objects with the given ids.

    Given a set of ids, get the objects from the DB

    :param user_id: User id
    :param workflow_id: Workflow ID (being manipulated)
    :param action_id: Action id (to be executed)
    :return: (user, action, log)
    """
    # Get the user
    user = None
    if user_id:
        user = get_user_model().objects.filter(id=user_id).first()
        if not user:
            raise Exception(
                ugettext('Unable to find user with id {0}').format(user_id),
            )

    workflow = None
    if workflow_id:
        workflow = models.Workflow.objects.filter(
            user=user,
            pk=workflow_id).first()
        if not workflow:
            raise Exception(
                ugettext('Unable to find workflow with id {0}').format(
                    workflow_id))

    action = None
    if action_id:
        # Get the action
        action = models.Action.objects.filter(
            workflow__user=user,
            pk=action_id).first()
        if not action:
            raise Exception(
                ugettext('Unable to find action with id {0}').format(
                    action_id))

    return user, workflow, action


def ontask_handler400(request: HttpRequest, exception) -> HttpResponse:
    """Return error 400."""
    response = render(request, '400.html', {})
    response.status_code = 400
    return response


def ontask_handler403(request: HttpRequest, exception) -> HttpResponse:
    """Return error 403."""
    response = render(request, '403.html', {})
    response.status_code = 403
    return response


def ontask_handler404(request: HttpRequest, exception) -> HttpResponse:
    """Return error 404."""
    response = render(request, '404.html', {})
    response.status_code = 404
    return response


def ontask_handler500(request: HttpRequest) -> HttpResponse:
    """Return error 500."""
    response = render(request, '500.html', {})
    response.status_code = 500
    return response
