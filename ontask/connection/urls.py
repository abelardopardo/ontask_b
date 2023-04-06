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
        views.SQLConnectionShowView.as_view(
            template_name='connection/includes/partial_show.html'),
        name='sqlconn_view'),

    path(
        '<int:pk>/sqlconn_clone/',
        views.SQLConnectionCloneView.as_view(),
        name='sqlconn_clone'),

    path(
        '<int:pk>/sqlconn_delete/',
        views.SQLConnectionDeleteView.as_view(),
        name='sqlconn_delete'),

    path(
        '<int:pk>/sqlconn_toggle/',
        views.SQLConnectionToggleView.as_view(),
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
        views.athena.AthenaConnectionCreateView.as_view(),
        name='athenaconn_create'),

    path(
        '<int:pk>/athenaconn_edit/',
        views.athena.AthenaConnectionEditView.as_view(),
        name='athenaconn_edit'),

    path(
        '<int:pk>/athenaconn_view/',
        views.athena.AthenaConnectionShowView.as_view(
            template_name='connection/includes/partial_show.html'),
        name='athenaconn_view'),

    path(
        '<int:pk>/athenaconn_clone/',
        views.athena.AthenaConnectionCloneView.as_view(),
        name='athenaconn_clone'),

    path(
        '<int:pk>/athenaconn_delete/',
        views.athena.AthenaConnectionDeleteView.as_view(),
        name='athenaconn_delete'),

    path(
        '<int:pk>/athenaconn_toggle/',
        views.athena.AthenaConnectionToggleView.as_view(),
        name='athenaconn_toggle'),
]
