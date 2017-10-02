# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

import ontask.views

from . import views

app_name = 'workflow'

urlpatterns = [
    url(r'^$', views.workflow_index, name='index'),

    url(r'^create/$', views.WorkflowCreateView.as_view(), name='create'),

    url(r'^(?P<pk>\d+)/update/$', views.update, name='update'),

    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),

    url(r'^(?P<pk>\d+)/flush/$', views.flush, name='flush'),

    url(r'^(?P<pk>\d+)/detail/$', views.WorkflowDetailView.as_view(),
        name='detail'),

    url(r'^attributes/$', views.attributes, name='attributes'),

    url(r'^attribute_create/$',
        views.attribute_create,
        name='attribute_create'),

    url(r'^attribute_delete/$',
        views.attribute_delete,
        name='attribute_delete'),

    url(r'^(?P<pk>\d+)/share/$', ontask.views.ToBeDone.as_view(), name='share'),

    url(r'^(?P<pk>\d+)/logs/$', ontask.views.ToBeDone.as_view(), name='logs'),

]
