"""First step to load data from a Google Sheet."""

from django.views import generic

from ontask.dataops.views import upload_steps
from ontask import models


class GoogleSheetUploadStart(upload_steps.UploadStepOneView, generic.FormView):
    step_1_url = 'dataops:googlesheetupload_start'
    log_upload = models.Log.WORKFLOW_DATA_GSHEET_UPLOAD
