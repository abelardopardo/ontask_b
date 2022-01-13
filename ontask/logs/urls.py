# -*- coding: utf-8 -*-

"""URLs to access the logs."""
from django.urls import path

from ontask.logs import api, views

app_name = 'logs'

urlpatterns = [
    path('', views.LogIndexView.as_view(), name='index'),

    path('index_ss/', views.LogIndexSSView.as_view(), name='index_ss'),

    path(
        '<int:pk>/modal_view/',
        views.LogDetailModalView.as_view(),
        name='modal_view'),

    path(
        '<int:pk>/page_view/',
        views.LogDetailView.as_view(),
        name='page_view'),

    path('<int:wid>/export/', views.LogExportView.as_view(), name='export'),

    path('list/', api.LogAPIList.as_view())]
