# -*- coding: utf-8 -*-

"""URLs to manipulate workflows, attributes, columns and shared."""

from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

import workflow.views.workflow_crud
from workflow import api, views

app_name = 'workflow'

urlpatterns = [
    path('create/', views.WorkflowCreateView.as_view(), name='create'),
    path('<int:wid>/clone/', views.clone_workflow, name='clone'),
    path('<int:wid>/update/', views.update, name='update'),
    path('<int:wid>/delete/', views.delete, name='delete'),
    path('<int:wid>/flush/', views.flush, name='flush'),
    path('<int:wid>/star/', views.star, name='star'),
    path('detail/', views.detail, name='detail'),
    path('operations/', views.operations, name='operations'),

    # Column table manipulation
    path('column_ss/', views.column_ss, name='column_ss'),

    # Import Export
    path(
        '<int:wid>/export_ask/',
        views.export_ask,
        name='export_ask'),
    re_path(
        r'(?P<page_data>\d+((,\d+)*))/export/',
        views.export,
        name='export'),
    path('import/', views.import_workflow, name='import'),

    # Attributes
    path(
        'attribute_create/',
        views.attribute_create,
        name='attribute_create'),
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

    # Column manipulation
    path('column_add/', views.column_add, name='column_add'),
    path('<int:pk>/question_add/', views.column_add, name='question_add'),
    path(
        'formula_column_add',
        views.formula_column_add,
        name='formula_column_add'),
    path(
        'random_column_add/',
        views.random_column_add,
        name='random_column_add'),
    path(
        '<int:pk>/column_delete/',
        views.column_delete,
        name='column_delete'),
    path('<int:pk>/column_edit/', views.column_edit, name='column_edit'),
    path(
        '<int:pk>/question_edit/',
        views.column_edit,
        name='question_edit'),
    path(
        '<int:pk>/column_clone/',
        views.column_clone,
        name='column_clone'),

    # Column movement
    path('column_move/', views.column_move, name='column_move'),
    path(
        '<int:pk>/column_move_top/',
        views.column_move_top,
        name='column_move_top'),
    path(
        '<int:pk>/column_move_bottom/',
        views.column_move_bottom,
        name='column_move_bottom'),
    path(
        '<int:pk>/column_restrict/',
        views.column_restrict_values,
        name='column_restrict'),

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
