"""View for the initial step to load data from an S3 bucket."""

from django.views import generic

from ontask.dataops.views import upload_steps
from ontask import models


class S3UploadStart(upload_steps.UploadStepOneView, generic.FormView):
    step_1_url = 'dataops:s3upload_start'
    log_upload = models.Log.WORKFLOW_DATA_S3_UPLOAD
