# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'profiles'

urlpatterns = [
    url(r'^me$', views.ShowProfile.as_view(), name='show_self'),
    url(r'^me/edit$', views.EditProfile.as_view(), name='edit_self'),
    url(r'^reset_token$', views.reset_token, name='reset_token'),
    url(r'^(?P<slug>[\w\-]+)$', views.ShowProfile.as_view(),
        name='show'),
]
