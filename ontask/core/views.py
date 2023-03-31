# -*- coding: utf-8 -*-

"""Basic views to render error."""
from django import http
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask import models, tasks
from ontask.core.decorators import ajax_required
from ontask.core.permissions import UserIsInstructor, is_admin, is_instructor
from ontask.django_auth_lti.decorators import lti_role_required
from ontask.workflow.views import WorkflowIndexView


class ToBeDone(UserIsInstructor, generic.TemplateView):
    """Page showing the to be done."""

    template_name = 'base.html'


def home(request: http.HttpRequest) -> http.HttpResponse:
    """Render the home page.

    :param request: Received HTTP Request
    :return: Rendered page.
    """
    if not request.user.is_authenticated:
        return redirect(reverse('accounts:login'))

    if is_instructor(request.user) or is_admin(request.user):
        return WorkflowIndexView.as_view()(request)

    # Authenticated request from learner, show profile
    return redirect(reverse('profiles:show_self'))


@login_required
@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Learner'])
def lti_entry(request: http.HttpRequest) -> http.HttpResponse:
    """Responde through LTI entry."""
    del request
    return redirect('home')


# No permissions in this URL as it is supposed to be wide open to track email
# reads.
def trck(request: http.HttpRequest) -> http.HttpResponse:
    """Receive a request with a token from email read tracking.

    :param request: Request object
    :return: Reflects in the DB the reception and (optionally) in the data
    table of the workflow
    """
    # Push the tracking to the asynchronous queue
    tasks.execute_operation.delay(
        operation_type=models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
        payload={'method': request.method, 'get_dict': request.GET})

    return http.HttpResponse(status=200)


@login_required
@csrf_exempt
@ajax_required
def keep_alive(request: http.HttpRequest) -> http.JsonResponse:
    """Return empty response to keep session alive.

    :param request:
    :return: Empty JSON response
    """
    del request
    return http.JsonResponse({})
