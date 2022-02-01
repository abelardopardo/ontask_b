"""URL to manipulate actions."""
from django.urls import path, re_path
from django.views.generic import TemplateView

from ontask import models
from ontask.action import forms, services, views


app_name = 'action'

urlpatterns = [
    #
    # Action CRUD
    #
    # List them all
    path('', views.ActionIndexView.as_view(), name='index'),
    path('<int:wid>/index/', views.ActionIndexView.as_view(), name='index_set'),

    # Create an action
    path(
        'create/',
        views.ActionCreateView.as_view(from_view=False),
        name='create'),
    path(
        '<int:fid>/create/',
        views.ActionCreateView.as_view(from_view=True),
        name='create_from_view'),

    # Update an action
    path('<int:pk>/update/', views.ActionUpdateView.as_view(), name='update'),

    # Clone the action
    path('<int:pk>/clone/', views.ActionCloneView.as_view(), name='clone'),

    # Edit action
    path('<int:pk>/edit/', views.action_edit, name='edit'),

    # Nuke the action
    path('<int:pk>/delete/', views.ActionDeleteView.as_view(), name='delete'),

    # Show timeline
    path(
        'timeline/',
        views.ActionShowTimelineView.as_view(),
        name='timeline'),
    path(
        '<int:pk>/timeline/',
        views.ActionShowTimelineView.as_view(single_action=True),
        name='timeline'),

    # Action export the file
    re_path(
        r'(?P<pklist>\d+(,\d+)*)/export/',
        views.ActionExportView.as_view(),
        name='export'),

    # Action import
    path('import/', views.ActionImportView.as_view(), name='import'),

    # Run action
    path('<int:pk>/run/', views.action_run_initiate, name='run'),

    # Run ZIP action
    path('<int:pk>/zip/', views.action_run_zip, name='zip_action'),

    # Personalised text and JSON action steps
    path(
        'item_filter/',
        views.ActionRunActionItemFilterView.as_view(),
        name='item_filter'),

    # Handling attachments in EMAIL REPORT
    path(
        '<int:pk>/<int:view_id>/add_attachment/',
        views.ActionAddRemoveAttachmentView.as_view(is_add_operation=True),
        name='add_attachment'),
    path(
        '<int:pk>/<int:view_id>/remove_attachment/',
        views.ActionAddRemoveAttachmentView.as_view(is_add_operation=False),
        name='remove_attachment'),

    # URL to use when action finishes run
    path('run_done/', views.action_run_finish, name='run_done'),
    path(
        'zip_export/',
        views.ActionZipExportView.as_view(),
        name='zip_export'),

    # ACTION IN EDIT PAGE
    # Manage columns for action in
    path(
        '<int:pk>/<int:cpk>/select_key_column_action/',
        views.ActionSelectColumnSurveyView.as_view(
            select_column=True,
            key_column=True),
        name='select_key_column_action'),
    path(
        '<int:pk>/unselect_key_column_action/',
        views.ActionSelectColumnSurveyView.as_view(),
        name='unselect_key_column_action'),

    # Select column for action in
    path(
        '<int:pk>/<int:cpk>/select_column_action/',
        views.ActionSelectColumnSurveyView.as_view(select_column=True),
        name='select_column_action'),

    # Unselect column for action in
    path(
        '<int:pk>/<int:cpk>/unselect_column_action/',
        views.ActionUnselectColumnSurveyView.as_view(),
        name='unselect_column_action'),

    # Toggle shuffle action-in
    path(
        '<int:pk>/shuffle_questions/',
        views.ActionShuffleQuestionsView.as_view(),
        name='shuffle_questions'),

    # Toggle question changes
    path(
        '<int:pk>/toggle_question_change/',
        views.ActionToggleQuestionChangeView.as_view(),
        name='toggle_question_change'),

    # Select condition for a column/question
    path(
        '<int:pk>/<int:condition_pk>/select_condition/',
        views.ActionSelectConditionQuestionView.as_view(),
        name='edit_in_select_condition'),
    path(
        '<int:pk>/select_condition/',
        views.ActionSelectConditionQuestionView.as_view(),
        name='edit_in_select_condition'),

    # Rubric URLs
    path(
        '<int:pk>/<int:cid>/<int:loa_pos>/rubric_cell_edit',
        views.ActionEditRubricCellView.as_view(),
        name='rubric_cell_edit'),

    # RUN SURVEY
    # Server side update of the run survey page for action in
    path(
        '<int:pk>/show_survey_table_ss/',
        views.ActionShowSurveyTableSSView.as_view(),
        name='show_survey_table_ss'),

    # Run action in a row. Can be executed by the instructor or a regular user
    path(
        '<int:pk>/run_survey_row/',
        views.ActionRunSurveyRowView.as_view(),
        name='run_survey_row'),

    # Say thanks
    path('thanks/', TemplateView.as_view(template_name='thanks.html')),

    # Preview action out
    path(
        '<int:pk>/<int:idx>/preview/',
        views.ActionPreviewView.as_view(),
        name='preview'),
    path(
        '<int:pk>/<int:idx>/preview_next_all_false/',
        views.ActionPreviewNextAllFalseView.as_view(),
        name='preview_all_false'),

    # Allow url on/off toggle
    path(
        '<int:pk>/showurl/',
        views.ActionShowURLView.as_view(),
        name='showurl'),

    # Serve the personalised content with accessing through LTI. The action
    # id must be given as parameter to guarantee a single URL point of entry
    path(
        'serve/',
        views.ActionServeActionLTIView.as_view(),
        name='serve_lti'),

    # Edit action description and name
    path(
        '<int:pk>/edit_description/',
        views.ActionEditDescriptionView.as_view(),
        name='edit_description'),
]


# PERSONALIZED TEXT
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.PERSONALIZED_TEXT,
    services.ActionEditProducerEmail.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_out.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.PERSONALIZED_TEXT,
    (
        services.ActionRunProducerEmail.as_view(
            form_class=forms.EmailActionRunForm,
            template_name='action/request_email_data.html'),
        services.ActionRunProducerEmail))

# EMAIL REPORT
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.EMAIL_REPORT,
    services.ActionEditProducerEmailReport.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_out.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.EMAIL_REPORT,
    (
        services.ActionRunProducerEmailReport.as_view(
            form_class=forms.SendListActionRunForm,
            template_name='action/request_email_report_data.html'),
        services.ActionRunProducerEmailReport))

# RUBRIC
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.RUBRIC_TEXT,
    services.ActionEditProducerRubric.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_rubric.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.RUBRIC_TEXT,
    (
        services.ActionRunProducerEmail.as_view(
            form_class=forms.EmailActionRunForm,
            template_name='action/request_email_data.html'),
        services.ActionRunProducerEmail))

# PERSONALIZED JSON
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.PERSONALIZED_JSON,
    services.ActionOutEditProducerBase.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_out.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.PERSONALIZED_JSON,
    (
        services.ActionRunProducerJSON.as_view(
            form_class=forms.JSONActionRunForm,
            template_name='action/request_json_data.html'),
        services.ActionRunProducerJSON))

# JSON REPORT
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.JSON_REPORT,
    services.ActionOutEditProducerBase.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_out.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.JSON_REPORT,
    (
        services.ActionRunProducerJSONReport.as_view(
            form_class=forms.JSONReportActionRunForm,
            template_name='action/request_json_report_data.html'),
        services.ActionRunProducerJSONReport))

# CANVAS PERSONALIZED EMAIL
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.PERSONALIZED_CANVAS_EMAIL,
    services.ActionEditProducerCanvasEmail.as_view(
        form_class=forms.EditActionOutForm,
        template_name='action/edit_out.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.PERSONALIZED_CANVAS_EMAIL,
    (
        services.ActionRunProducerCanvasEmail.as_view(
            form_class=forms.CanvasEmailActionRunForm,
            template_name='action/request_canvas_email_data.html'),
        services.ActionRunProducerCanvasEmail))

# ZIP action
# ------------------------------------------------------------------------------
services.ACTION_RUN_FACTORY.register_producer(
    models.action.ZIP_OPERATION,
    (
        services.ActionRunProducerZip.as_view(
            form_class=forms.ZipActionRunForm,
            template_name='action/action_zip_step1.html'),
        services.ActionRunProducerZip))

# SURVEY
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.SURVEY,
    services.ActionEditProducerSurvey.as_view(
        template_name='action/edit_in.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.SURVEY,
    (
        services.ActionRunProducerSurvey.as_view(
            template_name='action/run_survey.html'),
        None))

# TODO_LIST action
# ------------------------------------------------------------------------------
services.ACTION_EDIT_FACTORY.register_producer(
    models.Action.TODO_LIST,
    services.ActionEditProducerSurvey.as_view(
        template_name='action/edit_in.html'))

services.ACTION_RUN_FACTORY.register_producer(
    models.Action.TODO_LIST,
    (
        services.ActionRunProducerTODO.as_view(
            template_name='action/run_survey.html'),
        None))
