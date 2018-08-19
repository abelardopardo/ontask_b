# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

from . import views, resources, api

app_name = 'logs'

urlpatterns = [

    url(r'^$', views.display, name="index"),

    url(r'^display_ss/$', views.display_ss, name="display_ss"),

    url(r'^(?P<pk>\d+)/view/$', views.view, name="view"),

    url(r'^(?P<pk>\d+)/export/$', resources.export, name="export"),

    url(r'^list/$', api.LogAPIList.as_view()),

]
