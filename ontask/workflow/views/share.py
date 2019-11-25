# -*- coding: utf-8 -*-

"""Views to create and delete a "share" item for a workflow."""

from typing import Optional

from django import http
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.urls import reverse

from ontask import models
from ontask.core.decorators import ajax_required, get_workflow
from ontask.core.permissions import is_instructor
from ontask.workflow.forms import SharedForm


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='shared')
def share_create(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Add a new user to the list of those sharing the workflow.

    :param request: Http request received
    :param workflow: Workflow object being used
    :return: JSON response
    """
    # Create the form object with the form_fields just computed
    form = SharedForm(
        request.POST or None,
        user=request.user,
        workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # proceed with the update
        workflow.shared.add(form.user_obj)
        workflow.save()
        workflow.log(
            request.user,
            models.Log.WORKFLOW_SHARE_ADD,
            share_email=form.user_obj.email)
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_share_create.html',
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='shared')
def share_delete(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Delete one of the users sharing the workflow.

    :param request: Http Request
    :param pk: Primery key of the user to remove
    :param workflow: Workflow object being used
    :return: JSON response after removing the user.
    """
    # If the user does not exist, go back to home page
    user = get_user_model().objects.filter(id=pk).first()
    if not user:
        return http.JsonResponse({'html_redirect': reverse('home')})

    if request.method == 'POST':
        workflow.shared.remove(user)
        workflow.save()
        workflow.log(
            request.user,
            models.Log.WORKFLOW_SHARE_DELETE,
            share_email=user.email)
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_share_delete.html',
            {'uid': pk, 'uemail': user.email},
            request=request),
    })
