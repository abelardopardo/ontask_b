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
    url(r'^(?P<pk>\d+)/create_email/$',
        views.email_create,
        name="create_email"),

    url(r'^finish_schedule/$',
        views.scheduler_finalize_action,
        name='finish_schedule'),

    # Edit scheduled email action
    url(r'^(?P<pk>\d+)/edit_email/$', views.edit_email, name='edit_email'),

    # Deletell scheduled email action
    url(r'^(?P<pk>\d+)/delete_email/$',
        views.delete_email,
        name='delete_email'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
