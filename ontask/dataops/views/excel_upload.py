"""View to start the Excel upload process."""

from django.views import generic

from ontask.dataops.views import upload_steps
from ontask import models


class ExcelUploadStart(upload_steps.UploadStepOneView, generic.FormView):
    step_1_url = 'dataops:excel_upload_start'
    log_upload = models.Log.WORKFLOW_DATA_EXCEL_UPLOAD
