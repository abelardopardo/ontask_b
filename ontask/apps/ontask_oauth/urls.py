# -*- coding: utf-8 -*-

from django.urls import path

from ontask_oauth import views

app_name = 'ontask_oauth'

urlpatterns = [
    # OAuth call back url (to redirect to another page)
    path('callback/', views.callback, name='callback'),
]
