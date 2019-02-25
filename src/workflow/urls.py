# -*- coding: utf-8 -*-


from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import attribute_views, column_views, import_export_views, share_views, \
    views, api

app_name = 'workflow'

urlpatterns = [
    path('create/', views.WorkflowCreateView.as_view(), name='create'),

    path('<int:pk>/clone/', views.clone, name='clone'),

    path('<int:pk>/update/', views.update, name='update'),

    path('<int:pk>/delete/', views.delete, name='delete'),

    path('<int:pk>/flush/', views.flush, name='flush'),

    path('<int:pk>/detail/', views.WorkflowDetailView.as_view(),
         name='detail'),

    path('<int:pk>/operations/', views.operations, name='operations'),

    # Column table manipulation
    path('<int:pk>/column_ss/', views.column_ss, name='column_ss'),

    # Import Export
    path('<int:pk>/export_ask/',
         import_export_views.export_ask,
         name='export_ask'),

    re_path('(?P<data>(\d+(,\d+)*)?)/export/',
         import_export_views.export,
         name='export'),

    path('import/', import_export_views.import_workflow, name='import'),

    # Attributes
    path('attribute_create/',
         attribute_views.attribute_create,
         name='attribute_create'),

    path('<int:pk>/attribute_edit/',
         attribute_views.attribute_edit,
         name='attribute_edit'),

    path('<int:pk>/attribute_delete/',
         attribute_views.attribute_delete,
         name='attribute_delete'),

    # Sharing
    path('share_create/',
         share_views.share_create,
         name='share_create'),

    path('<int:pk>/share_delete/',
         share_views.share_delete,
         name='share_delete'),

    # Column manipulation
    path('column_add/', column_views.column_add, name='column_add'),

    path('<int:pk>/question_add/', column_views.column_add, name='question_add'),

    path('formula_column_add',
         column_views.formula_column_add,
         name='formula_column_add'),

    path('random_column_add/',
         column_views.random_column_add,
         name='random_column_add'),

    path('<int:pk>/column_delete/',
         column_views.column_delete,
         name='column_delete'),

    path('<int:pk>/column_edit/',
         column_views.column_edit,
         name='column_edit'),

    path('<int:pk>/question_edit/',
        column_views.column_edit,
        name='question_edit'),

    path('<int:pk>/column_clone/',
         column_views.column_clone,
         name='column_clone'),

    # Select key column for action in
    path('column_move/', column_views.column_move, name='column_move'),

    path('<int:pk>/column_move_top/',
         column_views.column_move_top,
         name='column_move_top'),

    path('<int:pk>/column_move_bottom/',
         column_views.column_move_bottom,
         name='column_move_bottom'),

    path('<int:pk>/column_restrict/',
         column_views.column_restrict_values,
         name='column_restrict'),

    # API

    # Listing and creating workflows
    path('workflows/',
         api.WorkflowAPIListCreate.as_view(),
         name='api_workflows'),

    # Get, update content or destroy workflows
    path('<int:pk>/rud/',
         api.WorkflowAPIRetrieveUpdateDestroy.as_view(),
         name='api_rud'),

    # Manage workflow locks (get, set (post, put), unset (delete))
    path('<int:pk>/lock/',
         api.WorkflowAPILock.as_view(),
         name='api_lock'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
