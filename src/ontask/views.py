# -*- coding: utf-8 -*-

"""Basic views to render error."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from django_auth_lti.decorators import lti_role_required
from ontask.permissions import UserIsInstructor, is_admin, is_instructor
from ontask.tasks import increase_track_count
from workflow.views import index


def home(request: HttpRequest) -> HttpResponse:
    """Render the home page."""
    if not request.user.is_authenticated:
        # Unauthenticated request, go to login
        return redirect(reverse('accounts:login'))

    if is_instructor(request.user) or is_admin(request.user):
        # Authenticated request, go to the workflow index
        return index(request)

    # Authenticated request from learner, show profile
    return redirect(reverse('profiles:show_self'))


class AboutPage(generic.TemplateView):
    """ABout page."""

    template_name = 'about.html'


class ToBeDone(UserIsInstructor, generic.TemplateView):
    """Page showing the to be done."""

    template_name = 'base.html'


@login_required
def entry(request):
    """Entry point."""
    return redirect('home')


@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student'])
def lti_entry(request):
    """Enter the application through LTI."""
    return redirect('home')


# No permissions in this URL as it is supposed to be wide open to track email
#  reads.
def trck(request):
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
def keep_alive(request):
    """Return empty response to keep session alive.

    :param request:

    :return:
    """
    return JsonResponse({})


@login_required
def under_construction(request):
    """Produce a page saying that this is under construction.

    :param request: Request object

    :return: HTML response
    """
    return render(request, 'under_construction.html', {})


def ontask_handler400(request, exception):
    """Return error 400."""
    response = render(request, '400.html', {})
    response.status_code = 400
    return response


def ontask_handler403(request, exception):
    """Return error 403."""
    response = render(request, '403.html', {})
    response.status_code = 403
    return response


def ontask_handler404(request, exception):
    """Return error 404."""
    response = render(request, '404.html', {})
    response.status_code = 404
    return response


def ontask_handler500(request):
    """Return error 500."""
    response = render(request, '500.html', {})
    response.status_code = 500
    return response
