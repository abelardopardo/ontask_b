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

    # SQL Upload/Merge
    path(
        '<int:pk>/sqlupload_start/',
        views.sqlupload_start,
        name='sqlupload_start'),

    # Upload/Merge
    path('upload_s2/', views.upload_s2, name='upload_s2'),

    path('upload_s3/', views.upload_s3, name='upload_s3'),

    path('upload_s4/', views.upload_s4, name='upload_s4'),

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
