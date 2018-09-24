# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, api

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

    #
    # API
    #

    # Listing and creating workflows
    url(r'^scheduled_email/$',
        api.ScheduledActionEmailAPIListCreate.as_view(),
        name='api_scheduled_email'),
    url(r'^scheduled_json/$',
        api.ScheduledActionJSONAPIListCreate.as_view(),
        name='api_scheduled_json'),

    # Get, update content or destroy scheduled actions
    url(r'^(?P<pk>\d+)/rud_email/$',
        api.ScheduledEmailAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_email'),
    url(r'^(?P<pk>\d+)/rud_json/$',
        api.ScheduledJSONAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_json'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
