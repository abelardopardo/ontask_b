# -*- coding: utf-8 -*-

"""URLs to manipulate connections."""
from django.urls import path

from ontask.connection import views

app_name = 'connection'
urlpatterns = [
    # SQL Connections
    path(
        'sqlconns_admin',
        views.sql_connection_admin_index,
        name='sqlconns_admin_index'),

    path(
        'sqlconns_instructor/',
        views.sql_connection_index,
        name='sqlconns_index'),

    path(
        'sqlconn_add/',
        views.sql_connection_edit,
        name='sqlconn_add'),

    path(
        '<int:pk>/sqlconn_edit/',
        views.sql_connection_edit,
        name='sqlconn_edit'),

    path(
        '<int:pk>/sqlconn_view/',
        views.sql_connection_view,
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_clone/',
        views.sql_connection_clone,
        name='sqlconn_clone'),

    path(
        '<int:pk>/sqlconn_delete/',
        views.sql_connection_delete,
        name='sqlconn_delete'),

    path(
        '<int:pk>/sqlconn_toggle/',
        views.sqlconn_toggle,
        name='sqlconn_toggle'),

    # Athena Connections
    # path(
    #     'athenaconns_admin',
    #     views.athena_connection_admin_index,
    #     name='athenaconns_admin_index'),
    #
    # path(
    #     'athenaconns_instructor/',
    #     views.athena_connection_instructor_index,
    #     name='athenaconns_instructor_index'),
    #
    # path(
    #     'athenaconn_add/',
    #     views.athena_connection_edit,
    #     name='athenaconn_add'),
    #
    # path(
    #     '<int:pk>/athenaconn_edit/',
    #     views.athena_connection_edit,
    #     name='athenaconn_edit'),
    #
    # path(
    #     '<int:pk>/athenaconn_view/',
    #     views.athena_connection_view,
    #     name='athenaconn_view'),
    #
    # path(
    #     '<int:pk>/athenaconn_clone/',
    #     views.athena_connection_clone,
    #     name='athenaconn_clone'),
    #
    # path(
    #     '<int:pk>/athenaconn_delete/',
    #     views.athena_connection_delete,
    #     name='athenaconn_delete'),
    #
    # path(
    #     '<int:pk>/athenaupload_start/',
    #     views.athenaupload_start,
    #     name='athenaupload_start'),
    #
    # path(
    #     '<int:pk>/athenaconn_toggle/',
    #     views.athenaconn_toggle,
    #     name='athenaconn_toggle'),
]
