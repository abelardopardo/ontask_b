# -*- coding: utf-8 -*-

"""URLs to manipulate the table."""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask.table import api, views
from ontask.table.views import stats

app_name = 'table'

urlpatterns = [

    #
    # API JSON
    #
    path('<int:wid>/ops/', api.TableJSONOps.as_view(), name='api_ops'),
    path('<int:wid>/merge/', api.TableJSONMerge.as_view(), name='api_merge'),

    #
    # API PANDAS
    #
    path('<int:wid>/pops/', api.TablePandasOps.as_view(), name='api_pops'),
    path(
        '<int:wid>/pmerge/',
        api.TablePandasMerge.as_view(),
        name='api_pmerge'),

    #
    # Display
    #
    path('', views.display, name='display'),
    path('display_ss/', views.display_ss, name='display_ss'),
    path(
        '<int:pk>/display_view/',
        views.display_view,
        name='display_view'),
    path(
        '<int:pk>/display_view_ss/',
        views.display_view_ss,
        name='display_view_ss'),
    path('row_delete/', views.row_delete, name='row_delete'),

    #
    # Views
    #
    path('view_add/', views.view_add, name='view_add'),
    path('<int:pk>/view_edit/', views.view_edit, name='view_edit'),
    path('<int:pk>/view_clone/', views.view_clone, name='view_clone'),
    path('<int:pk>/view_delete/', views.view_delete, name='view_delete'),

    #
    # Stats
    #
    path('stat_table/', stats.stat_table_view, name='stat_table'),
    path(
        '<int:pk>/stat_table_view/',
        stats.stat_table_view,
        name='stat_table_view'),
    path(
        '<int:pk>/stat_column/',
        stats.stat_column,
        name='stat_column'),
    path(
        '<int:pk>/stat_column_JSON/',
        stats.stat_column_json,
        name='stat_column_JSON'),

    #
    # CSV Download
    #
    path('csvdownload/', views.csvdownload, name='csvdownload'),
    path(
        '<int:pk>/csvdownload/',
        views.csvdownload_view,
        name='csvdownload_view'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
