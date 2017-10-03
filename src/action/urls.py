# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

import ontask.views

from . import views_action, views_condition

app_name = 'action'

urlpatterns = [
    url(r'^$', views_action.action_index, name='index'),

    url(r'^create/$', views_action.ActionCreateView.as_view(), name='create'),

    url(r'^(?P<pk>\d+)/edit/$', views_action.edit_action, name='edit'),

    url(r'^(?P<pk>\d+)/delete/$', views_action.delete_action, name='delete'),

    url(r'^(?P<pk>\d+)/preview/$', views_action.preview, name='preview'),

    url(r'^(?P<pk>\d+)/create_filter/$',
        views_condition.FilterCreateView.as_view(),
        name='create_filter'),

    url(r'^(?P<pk>\d+)/edit_filter/$',
        views_condition.edit_filter,
        name='edit_filter'),

    url(r'^(?P<pk>\d+)/delete_filter/$',
        views_condition.delete_filter,
        name='delete_filter'),

    url(r'^(?P<pk>\d+)/create_condition/$',
        views_condition.ConditionCreateView.as_view(),
        name='create_condition'),

    url(r'^(?P<pk>\d+)/edit_condition/$',
        views_condition.edit_condition,
        name='edit_condition'),

    url(r'^(?P<pk>\d+)/delete_condition/$',
        views_condition.delete_condition,
        name='delete_condition'),


]
