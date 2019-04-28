# -*- coding: utf-8 -*-


from django.urls import path

from . import (
    views,
    csvupload,
    excelupload,
    sqlcon_views,
    googlesheetupload,
    upload,
    s3upload
)

app_name = 'dataops'
urlpatterns = [

    # Show the upload merge menu
    path('uploadmerge/', views.uploadmerge, name="uploadmerge"),

    # Show list of plugins
    path('transform/', views.transform_model, name="transform"),
    path('model/', views.transform_model, name="model"),

    # Show plugin diagnostics
    path('<int:pk>/plugin_diagnose/', views.diagnose, name="plugin_diagnose"),

    # Show detailed information about the plugin
    path('<int:pk>/plugin_moreinfo/', views.moreinfo, name="plugin_moreinfo"),

    # Plugin invocation
    path('<int:pk>/plugin_invoke/', views.plugin_invoke,
         name='plugin_invoke'),

    # Manual Data Entry
    path('rowupdate/', views.row_update, name="rowupdate"),

    path('rowcreate/', views.row_create, name="rowcreate"),

    # CSV Upload/Merge
    path('csvupload1/', csvupload.csvupload1, name='csvupload1'),

    # Excel Upload/Merge
    path('excelupload1/', excelupload.excelupload1, name='excelupload1'),

    # Google Sheet Upload/Merge
    path('googlesheetupload1/',
         googlesheetupload.googlesheetupload1,
         name='googlesheetupload1'),

    # S3 Bucket CSV Upload/Merge
    path('s3upload1/', s3upload.s3upload1, name='s3upload1'),

    # Upload/Merge
    path('upload_s2/', upload.upload_s2, name='upload_s2'),

    path('upload_s3/', upload.upload_s3, name='upload_s3'),

    path('upload_s4/', upload.upload_s4, name='upload_s4'),

    # SQL Connections
    path('sqlconns_admin',
         sqlcon_views.sqlconnection_admin_index,
         name='sqlconns_admin_index'),

    path('sqlconns_instructor/',
         sqlcon_views.sqlconnection_instructor_index,
         name="sqlconns_instructor_index"),

    path('sqlconn_add/', sqlcon_views.sqlconn_add, name="sqlconn_add"),

    path('<int:pk>/sqlconn_view/',
         sqlcon_views.sqlconn_view,
         name="sqlconn_view"),

    path('<int:pk>/sqlconn_edit/',
         sqlcon_views.sqlconn_edit,
         name="sqlconn_edit"),

    path('<int:pk>/sqlconn_clone/',
         sqlcon_views.sqlconn_clone,
         name="sqlconn_clone"),

    path('<int:pk>/sqlconn_delete/',
         sqlcon_views.sqlconn_delete,
         name="sqlconn_delete"),

    path('<int:pk>/sqlupload1/',
         sqlcon_views.sqlupload1,
         name="sqlupload1"),
]
