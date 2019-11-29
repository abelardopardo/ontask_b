# -*- coding: utf-8 -*-

"""Basic views to render error."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask import models, tasks
from ontask.core.decorators import ajax_required
from ontask.core.permissions import UserIsInstructor, is_admin, is_instructor
from ontask.django_auth_lti.decorators import lti_role_required
from ontask.workflow.views import index


class AboutPage(generic.TemplateView):
    """About page."""

    template_name = 'about.html'


class ToBeDone(UserIsInstructor, generic.TemplateView):
    """Page showing the to be done."""

    template_name = 'base.html'


def home(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    :param request: Received HTTP Request
    :return: Rendered page.
    """
    if not request.user.is_authenticated:
        return redirect(reverse('accounts:login'))

    if is_instructor(request.user) or is_admin(request.user):
        return index(request)

    # Authenticated request from learner, show profile
    return redirect(reverse('profiles:show_self'))


@login_required
@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Learner'])
def lti_entry(request: HttpRequest) -> HttpResponse:
    return redirect('home')


# No permissions in this URL as it is supposed to be wide open to track email
# reads.
def trck(request: HttpRequest) -> HttpResponse:
    """Receive a request with a token from email read tracking.

    :param request: Request object
    :return: Reflects in the DB the reception and (optionally) in the data
    table of the workflow
    """
    # Push the tracking to the asynchronous queue
    tasks.execute_operation.delay(
        operation_type=models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
        payload={'method': request.method, 'get_dict': request.GET})

    return HttpResponse(status=200)


@login_required
@csrf_exempt
@ajax_required
def keep_alive(request: HttpRequest) -> JsonResponse:
    """Return empty response to keep session alive.

    :param request:
    :return: Empty JSON response
    """
    return JsonResponse({})


