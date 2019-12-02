# -*- coding: utf-8 -*-

"""URLs to access the logs."""
from django.urls import path

from ontask.logs import api, resources, views

app_name = 'logs'

urlpatterns = [
    path('', views.display, name='index'),

    path('display_ss/', views.display_ss, name='display_ss'),

    path('<int:pk>/view/', views.view, name='view'),

    path('<int:wid>/export/', resources.export, name='export'),

    path('list/', api.LogAPIList.as_view()),
]
