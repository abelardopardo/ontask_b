# -*- coding: utf-8 -*-

"""Views to manipulate dataframes."""

from django.urls import path

from dataops.views import (
    csvupload_start, diagnose, excelupload_start, googlesheetupload_start,
    moreinfo, plugin_invoke, row_create, row_update, s3upload_start,
    sqlconn_add, sqlconn_delete, sqlconnection, sqlconnection_admin_index,
    sqlconnection_instructor_index, sqlupload_start, transform_model,
    upload_s2, upload_s3, upload_s4, uploadmerge, plugin_admin
)

app_name = 'dataops'
urlpatterns = [

    # Show the upload merge menu
    path('uploadmerge/', uploadmerge, name='uploadmerge'),

    # Show list of plugins
    path('plugin_admin/', plugin_admin, name='plugin_admin'),
    path('transform/', transform_model, name='transform'),
    path('model/', transform_model, name='model'),

    # Show plugin diagnostics
    path('<int:pk>/plugin_diagnose/', diagnose, name='plugin_diagnose'),

    # Show detailed information about the plugin
    path('<int:pk>/plugin_moreinfo/', moreinfo, name='plugin_moreinfo'),

    # Plugin invocation
    path(
        '<int:pk>/plugin_invoke/',
        plugin_invoke,
        name='plugin_invoke'),

    # Manual Data Entry
    path('rowupdate/', row_update, name='rowupdate'),

    path('rowcreate/', row_create, name='rowcreate'),

    # CSV Upload/Merge
    path('csvupload_start/', csvupload_start, name='csvupload_start'),

    # Excel Upload/Merge
    path('excelupload_start/', excelupload_start, name='excelupload_start'),

    # Google Sheet Upload/Merge
    path(
        'googlesheetupload_start/',
        googlesheetupload_start,
        name='googlesheetupload_start'),

    # S3 Bucket CSV Upload/Merge
    path('s3upload_start/', s3upload_start, name='s3upload_start'),

    # Upload/Merge
    path('upload_s2/', upload_s2, name='upload_s2'),

    path('upload_s3/', upload_s3, name='upload_s3'),

    path('upload_s4/', upload_s4, name='upload_s4'),

    # SQL Connections
    path(
        'sqlconns_admin',
        sqlconnection_admin_index,
        name='sqlconns_admin_index'),

    path(
        'sqlconns_instructor/',
        sqlconnection_instructor_index,
        name='sqlconns_instructor_index'),

    path('sqlconn_add/', sqlconn_add, name='sqlconn_add'),

    path(
        '<int:pk>/sqlconn_view/',
        sqlconnection.sqlconn_view,
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_edit/',
        sqlconnection.sqlconn_edit,
        name='sqlconn_edit'),

    path(
        '<int:pk>/sqlconn_clone/',
        sqlconnection.sqlconn_clone,
        name='sqlconn_clone'),

    path('<int:pk>/sqlconn_delete/', sqlconn_delete, name='sqlconn_delete'),

    path('<int:pk>/sqlupload_start/', sqlupload_start, name='sqlupload_start'),
]
