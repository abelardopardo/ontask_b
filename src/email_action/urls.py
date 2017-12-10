# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

from . import views

app_name = 'email_action'

urlpatterns = [

    # Request data to send email
    url(r'^(?P<pk>\d+)$', views.request_data, name="index"),

    # Schedule email
    url(r'^(?P<pk>\d+)/schedule_email/$',
        views.schedule_email,
        name="schedule_email"),

    url(r'^(?P<pk>\d+)/(?P<idx>\d+)/preview/$', views.preview, name='preview'),
]
