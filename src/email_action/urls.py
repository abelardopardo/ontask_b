# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'email_action'

urlpatterns = [

    url(r'^(?P<pk>\d+)$', views.request_data, name="index"),

    url(r'^(?P<pk>\d+)/preview/$', views.preview, name='preview'),
]
