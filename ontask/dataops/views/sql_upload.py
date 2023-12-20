"""Function to upload a data frame from an existing SQL connection object."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask.connection import forms
from ontask.dataops import services
from ontask.dataops.views import common


class SQLUploadStart(common.UploadStart, generic.UpdateView):
    """Load a data frame using a SQL connection.

    The four-step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set)

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step
    """

    def get_queryset(self):
        """This view should only consider enabled connections."""
        return self.model.objects.filter(enabled=True)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['connection'] = kwargs.pop('instance')
        return kwargs

    def form_valid(self, form):
        conn = self.get_object()
        run_params = self.object.get_missing_fields(form.cleaned_data)

        # Process SQL connection using pandas
        try:
            services.sql_upload_step_one(
                self.request,
                self.workflow,
                conn,
                run_params)
        except Exception as exc:
            messages.error(
                self.request,
                _('Unable to obtain data: {0}').format(str(exc)))
            return redirect('dataops:uploadmerge')

        return redirect('dataops:upload_s2')
