# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

import dataops.upload
import dataops.views
from . import views, csvupload, excelupload

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

    # Upload/Merge
    url(r'^upload_s2/$', dataops.upload.upload_s2, name='upload_s2'),

    url(r'^upload_s3/$', dataops.upload.upload_s3, name='upload_s3'),

    url(r'^upload_s4/$', dataops.upload.upload_s4, name='upload_s4'),

]
