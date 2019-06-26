# -*- coding: utf-8 -*-

"""Home  page view."""

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls.base import reverse

from ontask.permissions import is_admin, is_instructor
from ontask.apps.workflow.views.workflow_crud import index


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
