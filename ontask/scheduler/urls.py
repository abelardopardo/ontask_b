# -*- coding: utf-8 -*-

"""URLs for the scheduler package."""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask.scheduler import api
from ontask.scheduler import views

app_name = 'scheduler'

urlpatterns = [

    # List all schedule actions
    path('', views.index, name='index'),

    # Create scheduled action
    path(
        '<int:pk>/create_action_run/',
        views.create_action_run,
        name='create_action_run'),

    # # Create scheduled workflow op
    # path(
    #     'create_workflow_op/',
    #     views.create_workflow_op,
    #     name='create_workflow_op'),

    # Edit scheduled operation
    path(
        '<int:pk>/edit_scheduled_operation/',
        views.edit_scheduled_operation,
        name='edit_scheduled_operation'),

    # View the details of a scheduled operation
    path('<int:pk>/view/', views.view, name='view'),

    # Delete scheduled email action
    path('<int:pk>/delete/', views.delete, name='delete'),

    path(
        'finish_scheduling/',
        views.finish_scheduling,
        name='finish_scheduling'),

    # API
    path(
        'scheduled_email/',
        api.ScheduledActionEmailAPIListCreate.as_view(),
        name='api_scheduled_email'),

    path(
        'scheduled_json/',
        api.ScheduledActionJSONAPIListCreate.as_view(),
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
