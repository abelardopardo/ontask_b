# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'logs'

urlpatterns = [

    url(r'^show/$',
        # views.LogDatatablesView.as_view(),
        views.show,
        name="show"),

    url(r'^showf/$',
        views.LogFilteredListView.as_view(),
        name="showf"),

]
