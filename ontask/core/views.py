# -*- coding: utf-8 -*-

"""Basic views to render error."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask.core.decorators import ajax_required
from ontask.core.permissions import UserIsInstructor
from ontask.django_auth_lti.decorators import lti_role_required
from ontask.tasks import increase_track_count


class AboutPage(generic.TemplateView):
    """ABout page."""

    template_name = 'about.html'


class ToBeDone(UserIsInstructor, generic.TemplateView):
    """Page showing the to be done."""

    template_name = 'base.html'


@login_required
def entry(request: HttpRequest) -> HttpResponse:
    """Entry point."""
    return redirect('home')


@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student'])
def lti_entry(request: HttpRequest) -> HttpResponse:
    """Enter the application through LTI."""
    return redirect('home')


# No permissions in this URL as it is supposed to be wide open to track email
#  reads.
def trck(request: HttpRequest) -> HttpResponse:
    """Receive a request with a token from email read tracking.

    :param request: Request object

    :return: Reflects in the DB the reception and (optionally) in the data
    table of the workflow
    """
    # Push the tracking to the asynchronous queue
    increase_track_count.delay(request.method, request.GET)

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


@login_required
def under_construction(request: HttpRequest) -> HttpResponse:
    """Produce a page saying that this is under construction.

    :param request: Request object

    :return: HTML response
    """
    return render(request, 'under_construction.html', {})


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
