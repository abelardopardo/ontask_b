# -*- coding: utf-8 -*-
from django.urls import path

from . import views_action, views_condition, views_out

app_name = 'action'

urlpatterns = [
    #
    # Action CRUD
    #
    # List them all
    path('', views_action.action_index, name='index'),
    path('<int:pk>/index/', views_action.action_index_set, name='index_set'),

    # Create an action of type 0: in, 1: Out
    path('create', views_action.ActionCreateView.as_view(), name='create'),

    # Edit action Out
    path('<int:pk>/edit/', views_action.edit_action, name='edit'),

    # Save action out content
    path('<int:pk>/action_out_save_content/',
         views_action.action_out_save_content,
         name='action_out_save_content'),

    # Action export ask
    path('<int:pk>/export_ask/', views_action.export_ask, name='export_ask'),

    # Action export done
    path('<int:pk>/export_done/', views_action.export_done, name='export_done'),

    # Action export done
    path('<int:pk>/export_download/',
         views_action.export_download,
         name='export_download'),

    # Action import
    path('import/', views_action.action_import, name='import'),

    # Update an action
    path('<int:pk>/update/',
         views_action.ActionUpdateView.as_view(),
         name='update'),

    # Clone the action
    path('<int:pk>/clone/', views_action.clone, name='clone'),

    # Nuke the action
    path('<int:pk>/delete/', views_action.delete_action, name='delete'),

    # Run ZIP action
    path('<int:pk>/zip/', views_out.zip_action, name='zip_action'),

    # Run action IN
    path('<int:pk>/run/', views_action.run, name='run'),

    #
    # Personalised text and JSON action steps
    #
    path('item_filter/',
         views_out.run_action_item_filter,
         name='item_filter'),

    #
    # URL to get/set Canvas OAuth Token
    #
    path('canvas_token/',
         views_out.canvas_get_or_set_oauth_token,
         name='canvas_get_or_set_oauth_token'),

    #
    # URLs to use when action finishes run
    #
    path('email_done/', views_out.email_action_done, name='email_done'),
    path('zip_done/', views_out.zip_action_done, name='zip_done'),
    path('zip_export/', views_out.action_zip_export, name='zip_export'),
    path('json_done/', views_out.json_done, name='json_done'),
    path('canvas_email_done/',
         views_out.canvas_email_done,
         name='canvas_email_done'),

    #
    # ACTION IN EDIT PAGE
    #
    # Select key column for action in
    path('<int:apk>/<int:cpk>/<int:key>/select_column_action/',
         views_action.select_column_action,
         name='select_key_column_action'),

    # Select column for action in
    path('<int:apk>/<int:cpk>/select_column_action/',
         views_action.select_column_action,
         name='select_column_action'),

    # Unselect column for action in
    path('<int:apk>/<int:cpk>/unselect_column_action/',
         views_action.unselect_column_action,
         name='unselect_column_action'),

    # Toggle shuffle action-in
    path('<int:pk>/shuffle_questions/',
         views_action.shuffle_questions,
         name='shuffle_questions'),

    #
    # RUN SURVEY
    #
    # Server side update of the run survey page for action in
    path('<int:pk>/run_survey_ss/',
         views_action.run_survey_ss,
         name='run_survey_ss'),

    # Run action in a row. Can be executed by the instructor or the
    # learner!!
    path('<int:pk>/run_survey_row/',
         views_action.run_survey_row,
         name='run_survey_row'),

    # Say thanks
    path('thanks/', views_action.thanks, name='thanks'),

    #
    # Preview action out
    #
    path('<int:pk>/<int:idx>/preview/',
         views_out.preview_response,
         name='preview'),
    path('<int:pk>/<int:idx>/preview_next_all_false/',
         views_out.preview_next_all_false_response,
         name='preview_all_false'),

    # Allow url on/off toggle
    path('<int:pk>/showurl/', views_action.showurl, name='showurl'),

    #
    # Serve the personalised content
    #
    path('<int:action_id>/serve/', views_action.serve, name='serve'),

    #
    # DESCRIPTION
    #
    path('<int:pk>/edit_description/',
         views_action.edit_description,
         name='edit_description'),

    #
    # FILTERS
    #
    path('<int:pk>/create_filter/',
         views_condition.FilterCreateView.as_view(),
         name='create_filter'),

    path('<int:pk>/edit_filter/',
         views_condition.edit_filter,
         name='edit_filter'),

    path('<int:pk>/delete_filter/',
         views_condition.delete_filter,
         name='delete_filter'),

    #
    # CONDITIONS
    #
    path('<int:pk>/create_condition/',
         views_condition.ConditionCreateView.as_view(),
         name='create_condition'),

    path('<int:pk>/edit_condition/',
         views_condition.edit_condition,
         name='edit_condition'),

    path('<int:pk>/delete_condition/',
         views_condition.delete_condition,
         name='delete_condition'),

    # Clone the condition
    path('<int:pk>/clone_condition/',
         views_condition.clone,
         name='clone_condition'),
    path('<int:pk>/<int:action_pk>/clone_condition/',
         views_condition.clone,
         name='clone_condition'),
]
