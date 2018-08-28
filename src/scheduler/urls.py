# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'scheduler'

urlpatterns = [

    # List all schedule actions
    url(r'^$', views.index, name='index'),

    # Create scheduled email action
    url(r'^(?P<pk>\d+)/create/$', views.edit, name="create"),

    # Edit scheduled email action
    url(r'^(?P<pk>\d+)/edit/$', views.edit, name='edit'),

    # Deletell scheduled email action
    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),

    url(r'^finish_scheduling/$',
        views.finish_scheduling,
        name='finish_scheduling'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
