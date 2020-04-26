 # -*- coding: utf-8 -*-

"""URLs to manipulate workflows, attributes and shared."""
from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask import models
from ontask.tasks import task_execute_factory
from ontask.workflow import api, services, views
 from django.urls import path, re_path
 from rest_framework.urlpatterns import format_suffix_patterns

 from ontask import models
 from ontask.tasks import task_execute_factory
 from ontask.workflow import api, services, views

 app_name = 'workflow'

urlpatterns = [
    # CRUD
    path('create/', views.WorkflowCreateView.as_view(), name='create'),
    path('<int:wid>/clone/', views.clone_workflow, name='clone'),
    path('<int:wid>/update/', views.update, name='update'),
    path('<int:wid>/delete/', views.delete, name='delete'),
    path('<int:wid>/flush/', views.flush, name='flush'),
    path('<int:wid>/star/', views.star, name='star'),
    path('operations/', views.operations, name='operations'),

    # Import Export
    path(
        '<int:wid>/export_ask/',
        views.export_ask,
        name='export_ask'),
    path(
        '<int:wid>/export_list_ask/',
        views.export_list_ask,
        name='export_list_ask'),
    re_path(
        r'(?P<page_data>(\d+,)*\d*)/export/',
        views.export,
        name='export'),
    path('import/', views.import_workflow, name='import'),

    # Attributes
    path('attribute_create/', views.attribute_create, name='attribute_create'),
    path(
        '<int:pk>/attribute_edit/',
        views.attribute_edit,
        name='attribute_edit'),
    path(
        '<int:pk>/attribute_delete/',
        views.attribute_delete,
        name='attribute_delete'),

    # Sharing
    path('share_create/', views.share_create, name='share_create'),
    path(
        '<int:pk>/share_delete/',
        views.share_delete,
        name='share_delete'),

    # Assign learner user email column
    path(
        'assign_luser_column/',
        views.assign_luser_column,
        name='assign_luser_column'),
    path(
        '<int:pk>/assign_luser_column/',
        views.assign_luser_column,
        name='assign_luser_column'),

    # API
    # Listing and creating workflows
    path(
        'workflows/',
        api.WorkflowAPIListCreate.as_view(),
        name='api_workflows'),

    # Get, update content or destroy workflows
    path(
        '<int:pk>/rud/',
        api.WorkflowAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud'),

    # Manage workflow locks (get, set (post, put), unset (delete))
    path(
        '<int:pk>/lock/',
        api.WorkflowAPILock.as_view(),
        name='api_lock'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

task_execute_factory.register_producer(
    models.Log.WORKFLOW_UPDATE_LUSERS,
    services.ExecuteUpdateWorkflowLUser())
