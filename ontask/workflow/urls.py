# -*- coding: utf-8 -*-

"""URLs to manipulate workflows, attributes and shared."""
from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask import models
from ontask.tasks import task_execute_factory
from ontask.workflow import api, services, views

app_name = 'workflow'

urlpatterns = [
    # CRUD
    path('create/', views.WorkflowCreateView.as_view(), name='create'),
    path(
        '<int:wid>/update/',
        views.WorkflowUpdateView.as_view(),
        name='update'),
    path(
        '<int:wid>/delete/',
        views.WorkflowDeleteView.as_view(),
        name='delete'),
    path('<int:wid>/clone/', views.WorkflowCloneView.as_view(), name='clone'),
    path('<int:wid>/flush/', views.WorkflowFlushView.as_view(), name='flush'),
    path('<int:wid>/star/', views.WorkflowStar.as_view(), name='star'),
    path(
        'operations/',
        views.WorkflowOperationsView.as_view(),
        name='operations'),

    # Import Export
    path(
        '<int:wid>/export_ask/',
        views.WorkflowActionExportView.as_view(only_action_list=False),
        name='export_ask'),
    path(
        '<int:wid>/export_list_ask/',
        views.WorkflowActionExportView.as_view(only_action_list=True),
        name='export_list_ask'),
    re_path(
        r'(?P<page_data>(\d+,)*\d*)/export/',
        views.WorkflowExportDoneView.as_view(),
        name='export'),
    path('import/', views.WorkflowImportView.as_view(), name='import'),

    # Attributes
    path(
        'attribute_create/',
        views.WorkflowAttributeCreateView.as_view(),
        name='attribute_create'),
    path(
        '<int:pk>/attribute_edit/',
        views.WorkflowAttributeEditView.as_view(),
        name='attribute_edit'),
    path(
        '<int:pk>/attribute_delete/',
        views.WorkflowAttributeDeleteView.as_view(),
        name='attribute_delete'),

    # Sharing
    path(
        'share_create/',
        views.WorkflowShareCreateView.as_view(),
        name='share_create'),
    path(
        '<int:pk>/share_delete/',
        views.WorkflowShareDeleteView.as_view(),
        name='share_delete'),

    # Assign learner user email column
    path(
        'assign_luser_column/',
        views.WorkflowAssignLUserColumn.as_view(),
        name='remove_luser_column'),
    path(
        '<int:pk>/assign_luser_column/',
        views.WorkflowAssignLUserColumn.as_view(),
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
