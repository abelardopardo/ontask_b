"""Package with the dataops views."""
from ontask.dataops.views.athena_upload import AthenaUploadStart
from ontask.dataops.views.csv_upload import CSVUploadStart
from ontask.dataops.views.excel_upload import ExcelUploadStart
from ontask.dataops.views.googlesheet_upload import GoogleSheetUploadStart
from ontask.dataops.views.plugin_admin import (
    PluginDiagnoseView, PluginMoreInfoView, PluginAdminView, PluginToggleView)
from ontask.dataops.views.row import RowCreateView, RowUpdateView
from ontask.dataops.views.s3_upload import S3UploadStart
from ontask.dataops.views.sql_upload import SQLUploadStart
from ontask.dataops.views.transform import (
    PluginInvokeView, TransformModelShowView)
from ontask.dataops.views.upload_steps import (
    UploadStepTwoView, UploadStepThreeView, UploadStepFourView,
    UploadShowSourcesView, UploadStepOneView)
from ontask.dataops.views.canvas_upload import (
    CanvasUploadStart, canvas_upload_start_finish)
