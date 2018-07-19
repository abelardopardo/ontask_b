# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import api, views, stat_views

app_name = 'table'

urlpatterns = [

    #
    # API
    #
    url(r'^(?P<pk>\d+)/ops/$', api.TableJSONOps.as_view(), name="api_ops"),

    url(r'^(?P<pk>\d+)/merge/$', api.TableJSONMerge.as_view(),
        name="api_merge"),

    # PANDAS
    url(r'^(?P<pk>\d+)/pops/$', api.TablePandasOps.as_view(), name="api_pops"),

    url(r'^(?P<pk>\d+)/pmerge/$', api.TablePandasMerge.as_view(),
        name="api_pmerge"),

    #
    # Display
    #
    url(r'^$', views.display, name="display"),

    url(r'^display_ss/$', views.display_ss, name="display_ss"),

    url(r'^(?P<pk>\d+)/display_view/$',
        views.display_view,
        name="display_view"),

    url(r'^(?P<pk>\d+)/display_view_ss/$',
        views.display_view_ss,
        name="display_view_ss"),

    url(r'^row_delete/$', views.row_delete, name="row_delete"),

    #
    # Views
    #
    url(r'^view_index/$', views.view_index, name="view_index"),

    url(r'view_add/$', views.view_add, name="view_add"),

    url(r'^(?P<pk>\d+)/view_edit/$',
        views.view_edit,
        name="view_edit"),

    url(r'^(?P<pk>\d+)/view_clone/$',
        views.view_clone,
        name="view_clone"),

    url(r'^(?P<pk>\d+)/view_delete/$',
        views.view_delete,
        name="view_delete"),

    #
    # Stats
    #
    url(r'^stat_row/$', stat_views.stat_row, name="stat_row"),

    url(r'^(?P<pk>\d+)/stat_row_view/$',
        stat_views.stat_row_view,
        name="stat_row_view"),

    url(r'^(?P<pk>\d+)/stat_column/$',
        stat_views.stat_column,
        name="stat_column"),

    url(r'^stat_table/$', stat_views.stat_table, name="stat_table"),

    url(r'^(?P<pk>\d+)/stat_table_view/$',
        stat_views.stat_table_view,
        name="stat_table_view"),

    #
    # CSV Download
    #
    url(r'^csvdownload/$', views.csvdownload, name="csvdownload"),

    url(r'^(?P<pk>\d+)/csvdownload/$', views.csvdownload,
        name="csvdownload_view"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
