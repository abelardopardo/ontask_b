# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

import dataops.upload
from . import views
from . import csvupload

app_name = 'dataops'

urlpatterns = [

    url(r'^$', views.dataops, name="list"),

    url(r'^uploadmerge/$', views.uploadmerge, name="uploadmerge"),

    # Manual Data Entry
    url(r'^rowupdate/$', views.row_update, name="rowupdate"),

    url(r'^rowcreate/$', views.row_create, name="rowcreate"),

    # CSV Update/Merge
    url(r'^csvupload1/$', csvupload.csvupload1, name='csvupload1'),

    # Update/Merge
    url(r'^upload_s2/$', dataops.upload.upload_s2, name='upload_s2'),

    url(r'^upload_s3/$', dataops.upload.upload_s3, name='upload_s3'),

    url(r'^upload_s4/$', dataops.upload.upload_s4, name='upload_s4'),

]
