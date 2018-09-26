# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.urls import path

from . import views, resources, api

app_name = 'logs'

urlpatterns = [

    path('', views.display, name="index"),

    path('display_ss/', views.display_ss, name="display_ss"),

    path('<int:pk>/view/', views.view, name="view"),

    path('<int:pk>/export/', resources.export, name="export"),

    path('list/', api.LogAPIList.as_view()),

]
