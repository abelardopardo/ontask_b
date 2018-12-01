# -*- coding: utf-8 -*-


from django.urls import path

import dataops.upload
import dataops.views
from . import views, csvupload, excelupload, sqlcon_views, googlesheetupload

app_name = 'dataops'
urlpatterns = [

    # Show the upload merge menu
    path('uploadmerge/', views.uploadmerge, name="uploadmerge"),

    # Show list of plugins
    path('transform/', views.transform, name="transform"),

    # Show plugin diagnostics
    path('<int:pk>/plugin_diagnose/',
        views.diagnose,
        name="plugin_diagnose"),

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
    url(r'^googlesheetupload1/$',
        googlesheetupload.googlesheetupload1,
        name='googlesheetupload1'),

    # Upload/Merge
    path('upload_s2/', dataops.upload.upload_s2, name='upload_s2'),

    path('upload_s3/', dataops.upload.upload_s3, name='upload_s3'),

    path('upload_s4/', dataops.upload.upload_s4, name='upload_s4'),

    # SQL Connections
    path('sqlconns/', sqlcon_views.sqlconnection_index, name="sqlconns"),

    path('sqlconn_add/', sqlcon_views.sqlconn_add, name="sqlconn_add"),

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

