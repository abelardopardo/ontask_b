# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth import get_user_model
from django.core import signing
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required

import logs.ops
from action.models import Action
from dataops import pandas_db, ops
from email_action import settings
from ontask.permissions import UserIsInstructor


class HomePage(generic.TemplateView):
    template_name = "home.html"


class AboutPage(generic.TemplateView):
    template_name = "about.html"


class ToBeDone(UserIsInstructor, generic.TemplateView):
    template_name = "base.html"


@login_required
def entry(request):
    return redirect('workflow:index')
def ontask_handler400(request):
    return render(request, '400.html', {})


def ontask_handler403(request):
    return render(request, '403.html', {})


def ontask_handler404(request):
    return render(request, '404.html', {})


def ontask_handler500(request):
    return render(request, '500.html', {})
