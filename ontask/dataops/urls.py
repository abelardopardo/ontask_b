"""Views to manipulate dataframes."""
from django.urls import path

from ontask import models
from ontask.dataops import services, views
from ontask.tasks import task_execute_factory

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
        views.CSVUploadStart.as_view(),
        name='csvupload_start'),

    # Excel Upload/Merge
    path(
        'excel_upload_start/',
        views.ExcelUploadStart.as_view(),
        name='excel_upload_start'),

    # Google Sheet Upload/Merge
    path(
        'googlesheetupload_start/',
        views.GoogleSheetUploadStart.as_view(),
        name='googlesheetupload_start'),

    # S3 Bucket CSV Upload/Merge
    path(
        's3upload_start/',
        views.S3UploadStart.as_view(),
        name='s3upload_start'),

    # SQL Upload/Merge
    path(
        '<int:pk>/sqlupload_start/',
        views.SQLUploadStart.as_view(),
        name='sqlupload_start'),

    # Athena Upload/Merge
    path(
        '<int:pk>/athenaupload_start/',
        views.AthenaUploadStart.as_view(),
        name='athenaupload_start'),

    # Upload/Merge
    path('upload_s2/', views.UploadStepTwoView.as_view(), name='upload_s2'),

    path('upload_s3/', views.UploadStepThreeView.as_view(), name='upload_s3'),

    path('upload_s4/', views.UploadStepFourView.as_view(), name='upload_s4'),

]

task_execute_factory.register_producer(
    models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
    services.ExecuteIncreaseTrackCount())

task_execute_factory.register_producer(
    models.Log.PLUGIN_EXECUTE,
    services.ExecuteRunPlugin())

task_execute_factory.register_producer(
    models.Log.WORKFLOW_DATA_SQL_UPLOAD,
    services.ExecuteSQLUpload())
