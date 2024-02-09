"""Views to manipulate dataframes."""
from django.utils.translation import gettext as _
from django.urls import path, reverse

from ontask import models
from ontask.dataops import forms, views
from ontask.connection.forms import (
    SQLRequestConnectionParam, AthenaRequestConnectionParam)

app_name = 'dataops'
urlpatterns = [
    # Show the upload merge menu
    path(
        'uploadmerge/',
        views.UploadShowSourcesView.as_view(),
        name='uploadmerge'),

    # Show list of plugins
    path(
        'plugin_admin/',
        views.PluginAdminView.as_view(),
        name='plugin_admin'),
    path(
        'transform/',
        views.TransformModelShowView.as_view(is_model=False),
        name='transform'),
    path(
        'model/',
        views.TransformModelShowView.as_view(is_model=True),
        name='model'),

    # Show plugin diagnostics
    path(
        '<int:pk>/plugin_diagnose/',
        views.PluginDiagnoseView.as_view(),
        name='plugin_diagnose'),

    # Show detailed information about the plugin
    path(
        '<int:pk>/plugin_moreinfo/',
        views.PluginMoreInfoView.as_view(),
        name='plugin_moreinfo'),

    # Toggle plugin is_enabled
    path(
        '<int:pk>/plugin_toggle/',
        views.PluginToggleView.as_view(),
        name='plugin_toggle'),
    # Plugin invocation
    path(
        '<int:pk>/plugin_invoke/',
        views.PluginInvokeView.as_view(),
        name='plugin_invoke'),

    # Manual Data Entry
    path('rowupdate/', views.RowUpdateView.as_view(), name='rowupdate'),

    path('rowcreate/', views.RowCreateView.as_view(), name='rowcreate'),

    # CSV Upload/Merge
    path(
        'csvupload_start/',
        views.CSVUploadStart.as_view(
            form_class=forms.UploadCSVFileForm,
            template_name='dataops/upload1.html',
            data_type='CSV',
            data_type_select=_('CSV file')),
        name='csvupload_start'),

    # Excel Upload/Merge
    path(
        'excel_upload_start/',
        views.ExcelUploadStart.as_view(
            form_class=forms.UploadExcelFileForm,
            template_name='dataops/upload1.html',
            data_type='Excel',
            data_type_select=_('Excel file')),
        name='excel_upload_start'),

    # Google Sheet Upload/Merge
    path(
        'googlesheetupload_start/',
        views.GoogleSheetUploadStart.as_view(
            form_class=forms.UploadGoogleSheetForm,
            template_name='dataops/upload1.html',
            data_type='Google Sheet',
            data_type_select=_('Google Sheet URL')),
        name='googlesheetupload_start'),

    # S3 Bucket CSV Upload/Merge
    path(
        's3upload_start/',
        views.S3UploadStart.as_view(
            form_class=forms.UploadS3FileForm,
            template_name='dataops/upload1.html',
            data_type='S3 CSV',
            data_type_select=_('S3 CSV file')),
        name='s3upload_start'),

    # SQL Upload/Merge
    path(
        '<int:pk>/sqlupload_start/',
        views.SQLUploadStart.as_view(
            model=models.SQLConnection,
            template_name='dataops/sqlupload_start.html',
            data_type='SQL',
            form_class=SQLRequestConnectionParam,
            prev_step_url='connection:sqlconns_index',
            data_type_select=_('SQL connection')),
        name='sqlupload_start'),

    # Athena Upload/Merge
    path(
        '<int:pk>/athenaupload_start/',
        views.AthenaUploadStart.as_view(
            model=models.AthenaConnection,
            template_name='dataops/athenaupload_start.html',
            data_type='Athena',
            data_type_select=_('Athena connection'),
            form_class=AthenaRequestConnectionParam,
            prev_step_url='connection:athenaconns_index'),
        name='athenaupload_start'),

    # Canvas Course Enrollment Upload/Merge
    path(
        'canvas_course_enrollments_upload_start/',
        views.CanvasCourseEnrollmentsUploadStart.as_view(
            form_class=forms.UploadCanvasForm,
            template_name='dataops/upload1.html',
            data_type='Canvas Course Enrollment List',
            data_type_select=_('Canvas Course'),
            log_type=models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD),
        name='canvas_course_enrollments_upload_start'),

    # Canvas Course Quizzes Upload/Merge
    path(
        'canvas_course_quizzess_upload_start/',
        views.CanvasCourseQuizzesUploadStart.as_view(
            form_class=forms.UploadCanvasForm,
            template_name='dataops/upload1.html',
            data_type='Canvas Course Quizzes',
            data_type_select=_('Canvas Course'),
            log_type=models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD),
        name='canvas_course_quizzes_upload_start'),

    path(
        'canvas_upload_start_finish/',
        views.canvas_upload_start_finish,
        name='canvas_upload_start_finish'),

    # Upload/Merge
    path('upload_s2/', views.UploadStepTwoView.as_view(), name='upload_s2'),

    path('upload_s3/', views.UploadStepThreeView.as_view(), name='upload_s3'),

    path('upload_s4/', views.UploadStepFourView.as_view(), name='upload_s4'),
]
