# -*- coding: utf-8 -*-

"""URLs to manipulate the table."""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask.table import api, views
from ontask.table.views import stats

app_name = 'table'

urlpatterns = [

    #
    # Display
    #
    path('', views.TableDiplayCompleteView.as_view(), name='display'),
    path(
        'display_ss/',
        views.TableDisplayCompleteSSView.as_view(),
        name='display_ss'),
    path(
        '<int:pk>/display_view/',
        views.TableDisplayViewView.as_view(),
        name='display_view'),
    path(
        '<int:pk>/display_view_ss/',
        views.TableDisplayViewSSView.as_view(),
        name='display_view_ss'),
    path('row_delete/', views.TableRowDeleteView.as_view(), name='row_delete'),

    #
    # Views
    #
    path('view_add/', views.ViewAddView.as_view(), name='view_add'),
    path(
        '<int:pk>/view_edit/',
        views.ViewEditView.as_view(),
        name='view_edit'),
    path(
        '<int:pk>/view_delete/',
        views.ViewDeleteView.as_view(),
        name='view_delete'),
    path(
        '<int:pk>/view_clone/',
        views.ViewCloneView.as_view(),
        name='view_clone'),

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
        views.ColumnStatsView.as_view(),
        name='stat_column'),
    path(
        '<int:pk>/stat_column_JSON/',
        views.ColumnStatsModalView.as_view(),
        name='stat_column_JSON'),

    #
    # CSV Download
    #
    path('csvdownload/', views.csvdownload, name='csvdownload'),
    path(
        '<int:pk>/csvdownload/',
        views.csvdownload_view,
        name='csvdownload_view'),

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
]

# For Django REST
urlpatterns = format_suffix_patterns(urlpatterns)
