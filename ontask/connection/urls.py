"""URLs to manipulate connections."""
from django.urls import path
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.connection import views

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
        views.sql.SQLConnectionIndexView.as_view(
            template_name='connection/index.html',
            title=_('SQL Connections'),
            is_sql=True),
        name='sqlconns_index'),

    path(
        'sqlconn_create/',
        views.SQLConnectionCreateView.as_view(),
        name='sqlconn_create'),

    path(
        '<int:pk>/sqlconn_edit/',
        views.SQLConnectionEditView.as_view(),
        name='sqlconn_edit'),

    path(
        '<int:pk>/sqlconn_view/',
        views.ConnectionShowView.as_view(
            template_name='connection/includes/partial_show.html',
            model=models.SQLConnection),
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_clone/',
        views.ConnectionCloneView.as_view(
            model=models.SQLConnection),
        name='sqlconn_clone'),

    path(
        '<int:pk>/sqlconn_delete/',
        views.ConnectionDeleteView.as_view(
            model=models.SQLConnection),
        name='sqlconn_delete'),

    path(
        '<int:pk>/sqlconn_toggle/',
        views.ConnectionToggleView.as_view(
            model=models.SQLConnection),
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
        views.AthenaConnectionIndexView.as_view(
            template_name='connection/index.html',
            title=_('Athena Connections')),
        name='athenaconns_index'),

    path(
        'athenaconn_create/',
        views.AthenaConnectionCreateView.as_view(),
        name='athenaconn_create'),

    path(
        '<int:pk>/athenaconn_edit/',
        views.AthenaConnectionEditView.as_view(),
        name='athenaconn_edit'),

    path(
        '<int:pk>/athenaconn_view/',
        views.ConnectionShowView.as_view(
            template_name='connection/includes/partial_show.html',
            model=models.AthenaConnection),
        name='athenaconn_view'),

    path(
        '<int:pk>/athenaconn_clone/',
        views.ConnectionCloneView.as_view(
            model=models.AthenaConnection),
        name='athenaconn_clone'),

    path(
        '<int:pk>/athenaconn_delete/',
        views.ConnectionDeleteView.as_view(
            model=models.AthenaConnection),
        name='athenaconn_delete'),

    path(
        '<int:pk>/athenaconn_toggle/',
        views.ConnectionToggleView.as_view(
            model=models.AthenaConnection),
        name='athenaconn_toggle'),
]
