# -*- coding: utf-8 -*-

"""URLs to manipulate connections."""
from django.urls import path

from ontask.connection import views

from django.utils.translation import gettext_lazy as _

app_name = 'connection'
urlpatterns = [
    # SQL Connections
    path(
        'sqlconns_admin',
        views.SQLConnectionAdminIndexView.as_view(
            template_name='connection/index_admin.html',
            title=_('SQL Connections')),
        name='sqlconns_admin_index'),

    path(
        'sqlconns_instructor/',
        views.sql.sql_connection_index,
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
        views.sql_connection_toggle,
        name='sqlconn_toggle'),

    # Athena Connections
    path(
        'athenaconns_admin',
        views.AthenaConnectionAdminIndexView.as_view(
            template_name='connection/index_admin.html',
            title=_('Athena Connections')),
        name='athenaconns_admin_index'),

    path(
        'athenaconns_instructor/',
        views.athena_connection_instructor_index,
        name='athenaconns_index'),

    path(
        'athenaconn_add/',
        views.athena.athena_connection_edit,
        name='athenaconn_add'),

    path(
        '<int:pk>/athenaconn_edit/',
        views.athena.athena_connection_edit,
        name='athenaconn_edit'),

    path(
        '<int:pk>/athenaconn_view/',
        views.athena.athena_connection_view,
        name='athenaconn_view'),

    path(
        '<int:pk>/athenaconn_clone/',
        views.athena.athena_connection_clone,
        name='athenaconn_clone'),

    path(
        '<int:pk>/athenaconn_delete/',
        views.athena.athena_connection_delete,
        name='athenaconn_delete'),

    path(
        '<int:pk>/athenaconn_toggle/',
        views.athena.athenaconn_toggle,
        name='athenaconn_toggle'),
]
