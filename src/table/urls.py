# -*- coding: utf-8 -*-

"""URLs to manipulate the table."""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from table import api, stat_views, views

app_name = 'table'

urlpatterns = [

    #
    # API JSON
    #
    path('<int:pk>/ops/', api.TableJSONOps.as_view(), name='api_ops'),
    path('<int:pk>/merge/', api.TableJSONMerge.as_view(), name='api_merge'),

    #
    # API PANDAS
    #
    path('<int:pk>/pops/', api.TablePandasOps.as_view(), name='api_pops'),
    path(
        '<int:pk>/pmerge/',
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
    path('view_index/', views.view_index, name='view_index'),
    path('view_add/', views.view_add, name='view_add'),
    path('<int:pk>/view_edit/', views.view_edit, name='view_edit'),
    path('<int:pk>/view_clone/', views.view_clone, name='view_clone'),
    path('<int:pk>/view_delete/', views.view_delete, name='view_delete'),

    #
    # Stats
    #
    path('stat_row/', stat_views.stat_row_view, name='stat_row'),
    path(
        '<int:pk>/stat_row_view/',
        stat_views.stat_row_view,
        name='stat_row_view'),
    path(
        '<int:pk>/stat_column/',
        stat_views.stat_column,
        name='stat_column'),
    path(
        '<int:pk>/stat_column_JSON/',
        stat_views.stat_column_json,
        name='stat_column_JSON'),
    path('stat_table/', stat_views.stat_table_view, name='stat_table'),
    path(
        '<int:pk>/stat_table_view/',
        stat_views.stat_table_view,
        name='stat_table_view'),

    #
    # CSV Download
    #
    path('csvdownload/', views.csvdownload, name='csvdownload'),
    path('<int:pk>/csvdownload/', views.csvdownload, name='csvdownload_view'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
