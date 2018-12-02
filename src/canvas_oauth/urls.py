# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.urls import path

from . import views

app_name = 'canvas_oauth'

urlpatterns = [
    # Canvas call back url (to redirect to another page)
    path('callback/', views.callback, name='callback'),
]
