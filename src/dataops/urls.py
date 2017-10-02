# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views
from . import csvupload

app_name = 'dataops'

urlpatterns = [

    url(r'^$', views.dataops, name="list"),

    url(r'^rowfilter/$', views.row_filter, name="rowfilter"),

    url(r'^rowupdate/$', views.row_update, name="rowupdate"),

    url(r'^csvupload1/$', csvupload.csvupload1, name='csvupload1'),

    url(r'^csvupload2/$', csvupload.csvupload2, name='csvupload2'),

    url(r'^csvupload3/$', csvupload.csvupload3, name='csvupload3'),

    url(r'^csvupload4/$', csvupload.csvupload4, name='csvupload4'),

    # url(r'^csv_upload/$', views.csv_upload, name="csv_upload"),

    # url(r'^select_columns_to_upload/$',
    #  views.select_columns_to_upload,
    # name="select_columns_to_upload"),

]
