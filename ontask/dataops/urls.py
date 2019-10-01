# -*- coding: utf-8 -*-

"""Views to manipulate dataframes."""

from django.urls import path
from ontask.dataops import views

# from ontask.dataops.views import (
#     csvupload_start, diagnose, excelupload_start, googlesheetupload_start,
#     moreinfo, plugin_admin, plugin_invoke, plugin_toggle, row_create,
#     row_update, s3upload_start, sqlconn_add, sqlconn_delete, sqlconnection,
#     sqlconnection_admin_index, sqlconnection_instructor_index, sqlupload_start,
#     transform_model, upload_s2, upload_s3, upload_s4, uploadmerge,
# )

app_name = 'dataops'
urlpatterns = [

    # Show the upload merge menu
    path('uploadmerge/', views.uploadmerge, name='uploadmerge'),

    # Show list of plugins
    path('plugin_admin/', views.plugin_admin, name='plugin_admin'),
    path('transform/', views.transform_model, name='transform'),
    path('model/', views.transform_model, name='model'),

    # Show plugin diagnostics
    path('<int:pk>/plugin_diagnose/', views.diagnose, name='plugin_diagnose'),

    # Show detailed information about the plugin
    path('<int:pk>/plugin_moreinfo/', views.moreinfo, name='plugin_moreinfo'),

    # Toggle plugin is_enabled
    path('<int:pk>/plugin_toggle/', views.plugin_toggle, name='plugin_toggle'),
    # Plugin invocation
    path(
        '<int:pk>/plugin_invoke/',
        views.plugin_invoke,
        name='plugin_invoke'),

    # Manual Data Entry
    path('rowupdate/', views.row_update, name='rowupdate'),

    path('rowcreate/', views.row_create, name='rowcreate'),

    # CSV Upload/Merge
    path('csvupload_start/', views.csvupload_start, name='csvupload_start'),

    # Excel Upload/Merge
    path(
        'excelupload_start/',
        views.excelupload_start,
        name='excelupload_start'),

    # Google Sheet Upload/Merge
    path(
        'googlesheetupload_start/',
        views.googlesheetupload_start,
        name='googlesheetupload_start'),

    # S3 Bucket CSV Upload/Merge
    path('s3upload_start/', views.s3upload_start, name='s3upload_start'),

    # Upload/Merge
    path('upload_s2/', views.upload_s2, name='upload_s2'),

    path('upload_s3/', views.upload_s3, name='upload_s3'),

    path('upload_s4/', views.upload_s4, name='upload_s4'),

    # SQL Connections
    path(
        'sqlconns_admin',
        views.sqlconnection_admin_index,
        name='sqlconns_admin_index'),

    path(
        'sqlconns_instructor/',
        views.sqlconnection_instructor_index,
        name='sqlconns_instructor_index'),

    path('sqlconn_add/', views.sqlconn_add, name='sqlconn_add'),

    path(
        '<int:pk>/sqlconn_view/',
        views.sqlconnection.sqlconn_view,
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_edit/',
        views.sqlconnection.sqlconn_edit,
        name='sqlconn_edit'),

    path(
        '<int:pk>/sqlconn_clone/',
        views.sqlconnection.sqlconn_clone,
        name='sqlconn_clone'),

    path(
        '<int:pk>/sqlconn_delete/',
        views.sqlconn_delete,
        name='sqlconn_delete'),

    path(
        '<int:pk>/sqlupload_start/',
        views.sqlupload_start,
        name='sqlupload_start'),

    # Athena Connections
    path(
        'athenaconns_admin',
        views.athenaconnection_admin_index,
        name='athenaconns_admin_index'),

    path(
        'athenaconns_instructor/',
        views.athenaconnection_instructor_index,
        name='athenaconns_instructor_index'),

    path('athenaconn_add/', views.athenaconn_add, name='athenaconn_add'),

    path(
        '<int:pk>/athenaconn_view/',
        views.athenaconnection.athenaconn_view,
        name='athenaconn_view'),

    path(
        '<int:pk>/athenaconn_edit/',
        views.athenaconnection.athenaconn_edit,
        name='athenaconn_edit'),

    path(
        '<int:pk>/athenaconn_clone/',
        views.athenaconnection.athenaconn_clone,
        name='athenaconn_clone'),

    path(
        '<int:pk>/athenaconn_delete/',
        views.athenaconn_delete,
        name='athenaconn_delete'),

    path(
        '<int:pk>/athenaupload_start/',
        views.athenaupload_start,
        name='athenaupload_start'),
]
