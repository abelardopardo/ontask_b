# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import generic


class HomePage(generic.TemplateView):
    template_name = "home.html"


class AboutPage(generic.TemplateView):
    template_name = "about.html"


class ToBeDone(generic.TemplateView):
    template_name = "base.html"
