"""First step for CSV upload."""

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.dataops import forms
from ontask.dataops.views import common


class CSVUploadStart(common.UploadStart, generic.FormView):
    """Start the upload of a data frame from a CSV file.

    The four step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step
    """

    form_class = forms.UploadCSVFileForm
    template_name = 'dataops/upload1.html'

    dtype = 'CSV'
    dtype_select = _('CSV file')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        # Dictionary to populate gradually throughout the sequence of steps.
        # It is stored in the session.
        self.request.session['upload_data'] = {
            'initial_column_names': form.frame_info[0],
            'column_types': form.frame_info[1],
            'src_is_key_column': form.frame_info[2],
            'step_1': reverse('dataops:csvupload_start'),
            'log_upload': models.Log.WORKFLOW_DATA_CSV_UPLOAD}

        return redirect('dataops:upload_s2')
