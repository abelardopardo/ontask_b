"""First step for CSV upload."""
from io import TextIOWrapper

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ontask.dataops import services
from ontask.dataops.views import upload_steps


class CSVUploadStart(upload_steps.UploadStepOneView):
    # Step 1 of the CSV upload
    def form_valid(self, form):
        # Process CSV file using pandas read_csv
        try:
            self.data_frame = services.load_df_from_csvfile(
                TextIOWrapper(
                    form.cleaned_data['data_file'],
                    encoding=form.data.encoding),
                form.cleaned_data['skip_lines_at_top'],
                form.cleaned_data['skip_lines_at_bottom'])
        except Exception as exc:
            messages.error(
                self.request,
                _('File could not be processed ({0})').format(str(exc)))
            return redirect('dataops:uploadmerge')

        return super().form_valid(form)

