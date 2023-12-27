"""View to start the Excel upload process."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ontask.dataops import services
from ontask.dataops.views import upload_steps


class ExcelUploadStart(upload_steps.UploadStepOneView):
    # Step 1 of the CSV upload
    def form_valid(self, form):
        # Process Excel file using pandas read_excel
        try:
            self.data_frame = services.load_df_from_excelfile(
                form.files['data_file'],
                form.cleaned_data['sheet'])
        except Exception as exc:
            messages.error(
                self.request,
                _('File could not be processed: {0}').format(str(exc)))
            return redirect('dataops:uploadmerge')

        return super().form_valid(form)
