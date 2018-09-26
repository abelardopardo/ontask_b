# -*- coding: utf-8 -*-


from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, api

app_name = 'scheduler'

urlpatterns = [

    # List all schedule actions
    path('', views.index, name='index'),

    # Create scheduled email action
    path('<int:pk>/create/', views.edit, name="create"),

    # Edit scheduled email action
    path('<int:pk>/edit/', views.edit, name='edit'),

    # Deletell scheduled email action
    path('<int:pk>/delete/', views.delete, name='delete'),

    path('finish_scheduling/',
         views.finish_scheduling,
         name='finish_scheduling'),

    #
    # API
    #

    # Listing and creating workflows
    path('scheduled_email/',
         api.ScheduledActionEmailAPIListCreate.as_view(),
         name='api_scheduled_email'),
    path('scheduled_json/',
         api.ScheduledActionJSONAPIListCreate.as_view(),
         name='api_scheduled_json'),

    # Get, update content or destroy scheduled actions
    path('<int:pk>/rud_email/',
         api.ScheduledEmailAPIRetrieveUpdateDestroy.as_view(),
         name='api_rud_email'),
    path('<int:pk>/rud_json/',
         api.ScheduledJSONAPIRetrieveUpdateDestroy.as_view(),
         name='api_rud_json'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
