# -*- coding: utf-8 -*-

"""URL to manipulate actions."""
from django.urls import path, re_path
from django.views.generic import TemplateView

from ontask import models, tasks
from ontask.action import forms, services, views

app_name = 'action'

urlpatterns = [
    #
    # Action CRUD
    #
    # List them all
    path('', views.action_index, name='index'),
    path('<int:wid>/index/', views.action_index, name='index_set'),

    # Create an action
    path('create/', views.ActionCreateView.as_view(), name='create'),

    # Show timeline
    path('timeline/', views.show_timeline, name='timeline'),
    path('<int:pk>/timeline/', views.show_timeline, name='timeline'),

    # Edit action
    path('<int:pk>/edit/', views.edit_action, name='edit'),

    # Save action out content
    path('<int:pk>/save_text/', views.save_text, name='save_text'),

    # Action export the file
    re_path(
        r'(?P<pklist>\d+(,\d+)*)/export/',
        views.export,
        name='export'),

    # Action import
    path('import/', views.action_import, name='import'),

    # Update an action
    path('<int:pk>/update/', views.ActionUpdateView.as_view(), name='update'),

    # Clone the action
    path('<int:pk>/clone_action/', views.clone_action, name='clone_action'),

    # Nuke the action
    path('<int:pk>/delete/', views.delete_action, name='delete'),

    # Run action
    path('<int:pk>/run/', views.run_action, name='run'),

    # Run ZIP action
    path('<int:pk>/zip/', views.zip_action, name='zip_action'),

    #
    # Personalised text and JSON action steps
    #
    path('item_filter/', views.run_action_item_filter, name='item_filter'),

    #
    # URL to use when action finishes run
    #
    path('run_done/', views.run_done, name='run_done'),
    path('zip_export/', views.action_zip_export, name='zip_export'),

    #
    # ACTION IN EDIT PAGE
    #
    # Manage columns for action in
    path(
        '<int:pk>/<int:cpk>/<int:key>/select_column_action/',
        views.select_column_action,
        name='select_key_column_action'),
    path(
        '<int:pk>/select_column_action/',
        views.select_column_action,
        name='unselect_key_column_action'),

    # Select column for action in
    path(
        '<int:pk>/<int:cpk>/select_column_action/',
        views.select_column_action,
        name='select_column_action'),

    # Unselect column for action in
    path(
        '<int:pk>/<int:cpk>/unselect_column_action/',
        views.unselect_column_action,
        name='unselect_column_action'),

    # Toggle shuffle action-in
    path(
        '<int:pk>/shuffle_questions/',
        views.shuffle_questions,
        name='shuffle_questions'),

    # Toggle question changes
    path(
        '<int:pk>/toggle_question_change/',
        views.toggle_question_change,
        name='toggle_question_change'),

    # Select condition for a column/question
    path(
        '<int:pk>/<int:condpk>/select_condition/',
        views.select_condition_for_question,
        name='edit_in_select_condition'),
    path(
        '<int:tpk>/select_condition/',
        views.select_condition_for_question,
        name='edit_in_select_condition'),

    # Rubric URLs
    path(
        '<int:pk>/<int:cid>/<int:loa_pos>/rubriccell_edit',
        views.edit_rubric_cell,
        name='rubriccell_edit'),
    path(
        '<int:pk>/rubric_loas_edit',
        views.edit_rubric_loas,
        name='rubric_loas_edit'),

    #
    # RUN SURVEY
    #
    # Server side update of the run survey page for action in
    path(
        '<int:pk>/show_survey_table_ss/',
        views.show_survey_table_ss,
        name='show_survey_table_ss'),

    # Run action in a row. Can be executed by the instructor or the
    # learner!!
    path(
        '<int:pk>/run_survey_row/',
        views.run_survey_row,
        name='run_survey_row'),

    # Say thanks
    path('thanks/', TemplateView.as_view(template_name='thanks.html')),

    #
    # Preview action out
    #
    path(
        '<int:pk>/<int:idx>/preview/',
        views.preview_response,
        name='preview'),
    path(
        '<int:pk>/<int:idx>/preview_next_all_false/',
        views.preview_next_all_false,
        name='preview_all_false'),

    # Allow url on/off toggle
    path('<int:pk>/showurl/', views.showurl, name='showurl'),

    #
    # Serve the personalised content
    #
    path('<int:action_id>/serve/', views.serve_action, name='serve'),
    path('serve/', views.serve_action_lti, name='serve_lti'),

    #
    # Edit action description and name
    #
    path(
        '<int:pk>/edit_description/',
        views.edit_description,
        name='edit_description'),

    #
    # FILTERS
    #
    path(
        '<int:pk>/create_filter/',
        views.FilterCreateView.as_view(),
        name='create_filter'),
    path('<int:pk>/edit_filter/', views.edit_filter, name='edit_filter'),
    path('<int:pk>/delete_filter/', views.delete_filter, name='delete_filter'),

    #
    # CONDITIONS
    #
    path(
        '<int:pk>/create_condition/',
        views.ConditionCreateView.as_view(),
        name='create_condition'),
    path(
        '<int:pk>/edit_condition/',
        views.edit_condition,
        name='edit_condition'),
    path(
        '<int:pk>/delete_condition/',
        views.delete_condition,
        name='delete_condition'),

    # Clone the condition
    path(
        '<int:pk>/clone_condition/',
        views.clone_condition,
        name='clone_condition'),
    path(
        '<int:pk>/<int:action_pk>/clone_condition/',
        views.clone_condition,
        name='clone_condition'),
]


EMAIL_PRODUCER = services.ActionManagerEmail(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_out.html',
    run_form_class=forms.EmailActionRunForm,
    run_template='action/request_email_data.html',
    log_event=models.Log.ACTION_RUN_EMAIL)

EMAIL_LIST_PRODUCER = services.ActionManagerEmailList(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_out.html',
    run_form_class=forms.SendListActionRunForm,
    run_template='action/request_send_list_data.html',
    log_event=models.Log.ACTION_RUN_EMAIL_LIST)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.PERSONALIZED_TEXT,
    EMAIL_PRODUCER)
tasks.task_execute_factory.register_producer(
    models.Action.PERSONALIZED_TEXT,
    EMAIL_PRODUCER)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.EMAIL_LIST,
    EMAIL_LIST_PRODUCER)
tasks.task_execute_factory.register_producer(
    models.Action.EMAIL_LIST,
    EMAIL_LIST_PRODUCER)

RUBRIC_PRODUCER = services.ActionManagerRubric(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_rubric.html',
    run_form_class=forms.SendListActionRunForm,
    run_template='action/request_send_list_data.html',
    log_event=models.Log.ACTION_RUN_EMAIL)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.RUBRIC_TEXT,
    RUBRIC_PRODUCER)

tasks.task_execute_factory.register_producer(
    models.Action.RUBRIC_TEXT,
    RUBRIC_PRODUCER)

JSON_PRODUCER = services.ActionManagerJSON(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_out.html',
    run_form_class=forms.JSONActionRunForm,
    run_template='action/request_json_data.html',
    log_event=models.Log.ACTION_RUN_JSON)

JSON_LIST_PRODUCER = services.ActionManagerJSONList(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_out.html',
    run_form_class=forms.JSONListActionRunForm,
    run_template='action/request_json_list_data.html',
    log_event=models.Log.ACTION_RUN_JSON_LIST)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.PERSONALIZED_JSON,
    JSON_PRODUCER)

tasks.task_execute_factory.register_producer(
    models.Action.PERSONALIZED_JSON,
    JSON_PRODUCER)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.JSON_LIST,
    JSON_LIST_PRODUCER)

tasks.task_execute_factory.register_producer(
    models.Action.JSON_LIST,
    JSON_LIST_PRODUCER)

CANVAS_EMAIL_PRODUCER = services.ActionManagerCanvasEmail(
    edit_form_class=forms.EditActionOutForm,
    edit_template='action/edit_out.html',
    run_form_class=forms.CanvasEmailActionRunForm,
    run_template='action/request_canvas_email_data.html',
    log_event=models.Log.ACTION_RUN_CANVAS_EMAIL)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.PERSONALIZED_CANVAS_EMAIL,
    CANVAS_EMAIL_PRODUCER)

tasks.task_execute_factory.register_producer(
    models.Action.PERSONALIZED_CANVAS_EMAIL,
    CANVAS_EMAIL_PRODUCER)

services.ACTION_PROCESS_FACTORY.register_producer(
    models.action.ZIP_OPERATION,
    services.ActionManagerZip(
        run_form_class=forms.ZipActionRunForm,
        run_template='action/action_zip_step1.html',
        log_event=models.Log.ACTION_RUN_ZIP))

services.ACTION_PROCESS_FACTORY.register_producer(
    models.Action.SURVEY,
    services.ActionManagerSurvey(
        edit_template='action/edit_in.html',
        run_template='action/run_survey.html',
        log_event=models.Log.ACTION_SURVEY_INPUT))
