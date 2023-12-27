"""Function to upload a data frame from an existing SQL connection object."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ontask import models, OnTaskException
from ontask.dataops import services
from ontask.dataops.views import upload_steps


class SQLUploadStart(upload_steps.UploadStepOneView):
    """Load a data frame using a SQL connection.

    The process will populate the payload dictionary with the fields:

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step
    """
    # Store the SQL connections Queryset needed in various places
    sql_connections = None

    def __init__(self, **kwargs):
        """Store available connections"""
        super().__init__(**kwargs)
        if not (connections := models.SQLConnection.objects.filter(
            enabled=True)
        ):
            raise OnTaskException(
                _('Incorrect invocation of SQL Upload (zero connections)'))
        self.sql_connections = connections

    def get_form_kwargs(self):
        """Include sql_connections"""
        kwargs = super().get_form_kwargs()
        kwargs['sql_connections'] = self.sql_connections
        return kwargs

    def form_valid(self, form):
        # Process SQL connection using pandas
        try:
            connection = self.sql_connections.get(
                id=int(form.cleaned_data['sql_connection']))
            self.data_frame = services.load_df_from_sqlconnection(connection)
        except Exception as exc:
            messages.error(
                self.request,
                _('Unable to obtain data: {0}').format(str(exc)))
            return redirect('dataops:uploadmerge')

        return super().form_valid(form)
