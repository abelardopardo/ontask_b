"""First step for CSV upload."""

from django.views import generic

from ontask.dataops.views import upload_steps
from ontask import models


class CSVUploadStart(upload_steps.UploadStepOneView, generic.FormView):
    step_1_url = 'dataops:csvupload_start'
    log_upload = models.Log.WORKFLOW_DATA_CSV_UPLOAD
