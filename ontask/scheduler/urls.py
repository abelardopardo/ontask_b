# -*- coding: utf-8 -*-

"""URLs for the scheduler package."""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask import models
from ontask.scheduler import api, services, views

app_name = 'scheduler'

urlpatterns = [

    # List all schedule actions
    path('', views.index, name='index'),

    # Create scheduled action
    path(
        '<int:pk>/create_action_run/',
        views.create_action_run,
        name='create_action_run'),

    # Select a SQL connection
    path('select_sql/', views.sql_connection_index, name='select_sql'),

    # Create a SQL upload operation
    path('<int:pk>/sqlupload/', views.create_sql_upload, name='sqlupload'),

    # Edit scheduled operation
    path(
        '<int:pk>/edit_scheduled_operation/',
        views.edit_scheduled_operation,
        name='edit_scheduled_operation'),

    # Toggle scheduled enable
    path(
        '<int:pk>/schedule_toggle/',
        views.schedule_toggle,
        name='schedule_toggle'),

    # View the details of a scheduled operation
    path('<int:pk>/view/', views.view, name='view'),

    # Delete scheduled action
    path('<int:pk>/delete/', views.delete, name='delete'),

    path(
        'finish_scheduling/',
        views.finish_scheduling,
        name='finish_scheduling'),

    # API
    path(
        'scheduled_email/',
        api.ScheduledOperationEmailAPIListCreate.as_view(),
        name='api_scheduled_email'),

    path(
        'scheduled_json/',
        api.ScheduledOperationJSONAPIListCreate.as_view(),
        name='api_scheduled_json'),

    # Get, update content or destroy scheduled actions
    path(
        '<int:pk>/rud_email/',
        api.ScheduledEmailAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_email'),
    path(
        '<int:pk>/rud_json/',
        api.ScheduledJSONAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_json'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

EMAIL_PROCESSOR = services.ScheduledOperationSaveEmail()

services.schedule_crud_factory.register_producer(
    models.Action.PERSONALIZED_TEXT,
    EMAIL_PROCESSOR)

services.schedule_crud_factory.register_producer(
    models.Action.RUBRIC_TEXT,
    EMAIL_PROCESSOR)

services.schedule_crud_factory.register_producer(
    models.Action.PERSONALIZED_JSON,
    services.ScheduledOperationSaveJSON())

services.schedule_crud_factory.register_producer(
    models.Action.EMAIL_REPORT,
    services.ScheduledOperationSaveEmailReport())

services.schedule_crud_factory.register_producer(
    models.Action.JSON_REPORT,
    services.ScheduledOperationSaveJSONReport())

services.schedule_crud_factory.register_producer(
    models.Log.WORKFLOW_DATA_SQL_UPLOAD,
    services.ScheduledOperationSaveSQLUpload())
