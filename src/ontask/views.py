# -*- coding: utf-8 -*-


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from action import settings
from django_auth_lti.decorators import lti_role_required
from ontask.permissions import UserIsInstructor
from ontask.tasks import increase_track_count
from ontask.permissions import is_instructor, is_admin
from workflow.views import index


def home(request):
    if not request.user.is_authenticated:
        # Unauthenticated request, go to login
        return redirect(reverse('accounts:login'))

    if is_instructor(request.user) or is_admin(request.user):
        # Authenticated request, go to the workflow index
        return index(request)

    # Authenticated request from learner, show profile
    return redirect(reverse('profiles:show_self'))


class AboutPage(generic.TemplateView):
    template_name = "about.html"


class ToBeDone(UserIsInstructor, generic.TemplateView):
    template_name = "base.html"


@login_required
def entry(request):
    return redirect('home')


@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student'])
def lti_entry(request):
    return redirect('home')


# No permissions in this URL as it is supposed to be wide open to track email
#  reads.
def trck(request):
    """
    Receive a request with a token from email read tracking
    :param request: Request object
    :return: Reflects in the DB the reception and (optionally) in the data 
    table of the workflow
    """

    # Push the tracking to the asynchronous queue
    increase_track_count.delay(request.method, request.GET)

    return HttpResponse(settings.PIXEL, content_type='image/png')


@login_required
@csrf_exempt
def keep_alive(request):
    """
    Function invoked by the session Timeout Javascript fragment when the
    session is about to expire and the user clicks on "continue connected"
    :param request:
    :return:
    """
    return JsonResponse({})


@login_required
def under_construction(request):
    """
    Produce a page saying that this is under construction
    :param request: Request object
    :return: HTML response
    """

    return render(request, 'under_construction.html', {})


def ontask_handler400(request, exception):
    response = render(request, '400.html', {})
    response.status_code = 400
    return response


def ontask_handler403(request, exception):
    response = render(request, '403.html', {})
    response.status_code = 403
    return response


def ontask_handler404(request, exception):
    response = render(request, '404.html', {})
    response.status_code = 404
    return response


def ontask_handler500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response
