# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import api
from . import views

app_name = 'table'

urlpatterns = [

    #
    # API
    #
    # JSON
    url(r'^(?P<pk>\d+)/ops/$', api.TableJSONOps.as_view(), name="api_ops"),

    url(r'^(?P<pk>\d+)/merge/$', api.TableJSONMerge.as_view(),
        name="api_merge"),

    # PANDAS
    url(r'^(?P<pk>\d+)/pops/$', api.TablePandasOps.as_view(), name="api_pops"),

    url(r'^(?P<pk>\d+)/pmerge/$', api.TablePandasMerge.as_view(),
        name="api_pmerge"),

    #
    # Display
    #
    url(r'^display/$', views.display, name="display"),

    url(r'^display_ss/$', views.display_ss, name="display_ss"),

    url(r'^row_delete/$', views.row_delete, name="row_delete")
]

urlpatterns = format_suffix_patterns(urlpatterns)
