# -*- coding: utf-8 -*-

"""Views to manipulate dataframes."""
from django.urls import path

from ontask import models
from ontask.dataops import services, views
from ontask.tasks import task_execute_factory

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
        views.sql_connection_admin_index,
        name='sqlconns_admin_index'),

    path(
        'sqlconns_instructor/',
        views.sql_connection_index,
        name='sqlconns_index'),

    path(
        'sqlconn_add/',
        views.sql_connection_edit,
        name='sqlconn_add'),

    path(
        '<int:pk>/sqlconn_edit/',
        views.sql_connection_edit,
        name='sqlconn_edit'),

    path(
        '<int:pk>/sqlconn_view/',
        views.sql_connection_view,
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_clone/',
        views.sql_connection_clone,
        name='sqlconn_clone'),

    path(
        '<int:pk>/sqlconn_delete/',
        views.sql_connection_delete,
        name='sqlconn_delete'),

    path(
        '<int:pk>/sqlupload_start/',
        views.sqlupload_start,
        name='sqlupload_start'),

    path(
        '<int:pk>/sqlconn_toggle/',
        views.sqlconn_toggle,
        name='sqlconn_toggle'),

    # Athena Connections
    path(
        'athenaconns_admin',
        views.athena_connection_admin_index,
        name='athenaconns_admin_index'),

    path(
        'athenaconns_instructor/',
        views.athena_connection_instructor_index,
        name='athenaconns_instructor_index'),

    path(
        'athenaconn_add/',
        views.athena_connection_edit,
        name='athenaconn_add'),

    path(
        '<int:pk>/athenaconn_edit/',
        views.athena_connection_edit,
        name='athenaconn_edit'),

    path(
        '<int:pk>/athenaconn_view/',
        views.athena_connection_view,
        name='athenaconn_view'),

    path(
        '<int:pk>/athenaconn_clone/',
        views.athena_connection_clone,
        name='athenaconn_clone'),

    path(
        '<int:pk>/athenaconn_delete/',
        views.athena_connection_delete,
        name='athenaconn_delete'),

    path(
        '<int:pk>/athenaupload_start/',
        views.athenaupload_start,
        name='athenaupload_start'),

    path(
        '<int:pk>/athenaconn_toggle/',
        views.athenaconn_toggle,
        name='athenaconn_toggle'),
]

task_execute_factory.register_producer(
    models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
    services.ExecuteIncreaseTrackCount())

task_execute_factory.register_producer(
    models.Log.PLUGIN_EXECUTE,
    services.ExecuteRunPlugin())

task_execute_factory.register_producer(
    models.Log.WORKFLOW_DATA_SQL_UPLOAD,
    services.ExecuteSQLUpload())
