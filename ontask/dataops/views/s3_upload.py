"""View for the initial step to load data from an S3 bucket."""
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ontask.dataops import services
from ontask.dataops.views import upload_steps


class S3UploadStart(upload_steps.UploadStepOneView):
    # Step 1 of the S3 CSV upload
    def form_valid(self, form):
        # Process S3 file using pandas read_excel
        try:
            self.data_frame = services.load_df_from_s3(
                form.cleaned_data['aws_access_key'],
                form.cleaned_data['aws_secret_access_key'],
                form.cleaned_data['aws_bucket_name'],
                form.cleaned_data['aws_file_key'],
                form.cleaned_data['skip_lines_at_top'],
                form.cleaned_data['skip_lines_at_bottom'])
        except Exception as exc:
            messages.error(
                self.request,
                _('S3 bucket file could not be processed: {0}').format(
                    str(exc)))
            return redirect('dataops:uploadmerge')

        return super().form_valid(form)
