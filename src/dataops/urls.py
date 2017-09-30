# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'dataops'

urlpatterns = [

    url(r'^$', views.dataops, name="list"),

    url(r'^csvupload1/$', views.csvupload1, name='csvupload1'),

    url(r'^csvupload2/$', views.csvupload2, name='csvupload2'),

    url(r'^csvupload3/$', views.csvupload3, name='csvupload3'),

    url(r'^csvupload4/$', views.csvupload4, name='csvupload4'),

    # url(r'^csv_upload/$', views.csv_upload, name="csv_upload"),

    # url(r'^select_columns_to_upload/$',
    #  views.select_columns_to_upload,
    # name="select_columns_to_upload"),

]
