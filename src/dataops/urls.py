# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

import dataops.upload
import dataops.views
from . import views, csvupload, excelupload, sqlcon_views, googlesheetupload

app_name = 'dataops'
urlpatterns = [

    # Show the upload merge menu
    url(r'^uploadmerge/$', views.uploadmerge, name="uploadmerge"),

    # Show list of plugins
    url(r'^transform/$', views.transform, name="transform"),

    # Show plugin diagnostics
    url(r'^(?P<pk>\d+)/plugin_diagnose/$',
        views.diagnose,
        name="plugin_diagnose"),

    # Plugin invocation
    url(r'^(?P<pk>\d+)/plugin_invoke/$', views.run,
        name='plugin_invoke'),

    # Manual Data Entry
    url(r'^rowupdate/$', views.row_update, name="rowupdate"),

    url(r'^rowcreate/$', views.row_create, name="rowcreate"),

    # CSV Upload/Merge
    url(r'^csvupload1/$', csvupload.csvupload1, name='csvupload1'),

    # Excel Upload/Merge
    url(r'^excelupload1/$', excelupload.excelupload1, name='excelupload1'),

    # Google Sheet Upload/Merge
    url(r'^googlesheetupload1/$',
        googlesheetupload.googlesheetupload1,
        name='googlesheetupload1'),

    # Upload/Merge
    url(r'^upload_s2/$', dataops.upload.upload_s2, name='upload_s2'),

    url(r'^upload_s3/$', dataops.upload.upload_s3, name='upload_s3'),

    url(r'^upload_s4/$', dataops.upload.upload_s4, name='upload_s4'),

    # SQL Connections
    url(r'^sqlconns/$', sqlcon_views.sqlconnection_index, name="sqlconns"),

    url(r'sqlconn_add/$', sqlcon_views.sqlconn_add, name="sqlconn_add"),

    url(r'^(?P<pk>\d+)/sqlconn_edit/$',
        sqlcon_views.sqlconn_edit,
        name="sqlconn_edit"),

    url(r'^(?P<pk>\d+)/sqlconn_clone/$',
        sqlcon_views.sqlconn_clone,
        name="sqlconn_clone"),

    url(r'^(?P<pk>\d+)/sqlconn_delete/$',
        sqlcon_views.sqlconn_delete,
        name="sqlconn_delete"),

    url(r'^(?P<pk>\d+)/sqlupload1/$',
        sqlcon_views.sqlupload1,
        name="sqlupload1"),
]

