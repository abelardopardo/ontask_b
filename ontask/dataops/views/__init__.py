"""Package with the dataops views."""
from ontask.dataops.views.common import UploadStart
from ontask.dataops.views.athenaupload import AthenaUploadStart
from ontask.dataops.views.csvupload import CSVUploadStart
from ontask.dataops.views.excelupload import ExcelUploadStart
from ontask.dataops.views.googlesheetupload import GoogleSheetUploadStart
from ontask.dataops.views.plugin_admin import (
    PluginDiagnoseView, PluginMoreInfoView, PluginAdminView, PluginToggleView)
from ontask.dataops.views.row import RowCreateView, RowUpdateView
from ontask.dataops.views.s3upload import S3UploadStart
from ontask.dataops.views.sql_upload import SQLUploadStart
from ontask.dataops.views.transform import (
    PluginInvokeView, TransformModelShowView)
from ontask.dataops.views.upload_steps import (
    UploadStepTwoView, UploadStepThreeView, UploadStepFourView,
    UploadShowSourcesView)
from ontask.dataops.views.canvas_student_upload import (
    CanvasCourseStudentUploadStart)