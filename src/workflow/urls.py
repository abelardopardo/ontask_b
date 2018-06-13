# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import attribute_views, column_views, import_export_views, share_views, \
    views, api

app_name = 'workflow'

urlpatterns = [
    url(r'^$', views.workflow_index, name='index'),

    url(r'^create/$', views.WorkflowCreateView.as_view(), name='create'),

    url(r'^(?P<pk>\d+)/clone/$', views.clone, name='clone'),

    url(r'^(?P<pk>\d+)/update/$', views.update, name='update'),

    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),

    url(r'^(?P<pk>\d+)/flush/$', views.flush, name='flush'),

    url(r'^(?P<pk>\d+)/detail/$', views.WorkflowDetailView.as_view(),
        name='detail'),

    # Column table manipulation
    url(r'^(?P<pk>\d+)/column_ss/$', views.column_ss, name='column_ss'),

    # Import Export

    url(r'^export_ask/$', import_export_views.export_ask, name='export_ask'),

    url(r'^(?P<data>(\d+(,\d+)*)?)/export/$',
        import_export_views.export,
        name='export'),

    url(r'^import/$', import_export_views.import_workflow, name='import'),

    # Attributes

    url(r'^attributes/$', attribute_views.attributes, name='attributes'),

    url(r'^attribute_create/$',
        attribute_views.attribute_create,
        name='attribute_create'),

    url(r'^(?P<pk>\d+)/attribute_edit/$',
        attribute_views.attribute_edit,
        name='attribute_edit'),

    url(r'^(?P<pk>\d+)/attribute_delete/$',
        attribute_views.attribute_delete,
        name='attribute_delete'),

    # Sharing

    url(r'^share/$', share_views.share, name='share'),

    url(r'^share_create/$',
        share_views.share_create,
        name='share_create'),

    url(r'^(?P<pk>\d+)/share_delete/$',
        share_views.share_delete,
        name='share_delete'),

    # Column manipulation

    url(r'^column_add/$', column_views.column_add, name='column_add'),

    url(r'^formula_column_add/$',
        column_views.formula_column_add,
        name='formula_column_add'),

    url(r'^(?P<pk>\d+)/column_delete/$',
        column_views.column_delete,
        name='column_delete'),

    url(r'^(?P<pk>\d+)/column_edit/$',
        column_views.column_edit,
        name='column_edit'),

    url(r'^(?P<pk>\d+)/column_clone/$',
        column_views.column_clone,
        name='column_clone'),

    url(r'^(?P<pk>\d+)/column_move_prev/$',
        column_views.column_move_prev,
        name='column_move_prev'),

    url(r'^(?P<pk>\d+)/column_move_next/$',
        column_views.column_move_next,
        name='column_move_next'),

    url(r'^(?P<pk>\d+)/column_move_top/$',
        column_views.column_move_top,
        name='column_move_top'),

    url(r'^(?P<pk>\d+)/column_move_bottom/$',
        column_views.column_move_bottom,
        name='column_move_bottom'),

    url(r'^(?P<pk>\d+)/column_restrict/$',
        column_views.column_restrict_values,
        name='column_restrict'),

    # API

    url(r'^workflows/$', api.WorkflowAPIListCreate.as_view(),
        name='api_workflows'),

    url(r'^(?P<pk>\d+)/rud/$',
        api.WorkflowAPIRetrieveUpdateDestroy.as_view(), name='api_rud'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
