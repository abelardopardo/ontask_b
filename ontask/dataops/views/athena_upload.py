"""Function to upload a data frame from an Athena connection object."""

from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ontask import models, OnTaskException
from ontask.dataops.views import upload_steps


class AthenaUploadStart(upload_steps.UploadStepOneView):
    """Start the upload of a data frame through an Athena connection.

    The parameters are obtained and if valid, an operation is scheduled for
    execution.
    """

    # Store the Athena connections Queryset needed in various places
    athena_connections = None

    def __init__(self, **kwargs):
        """Store available connections"""
        super().__init__(**kwargs)
        if not (connections := models.AthenaConnection.objects.filter(
            enabled=True)
        ):
            raise OnTaskException(
                _('Incorrect invocation of Athena Upload (zero connections)'))
        self.sql_connections = connections

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['athena_connections'] = self.athena_connections
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.athena_connections) == 1:
            context['only_athena_connection_name'] = (
                self.athena_connections.first().name)
        return context

    def form_valid(self, form):
        # Batch execution -- SEE SQLUploadStart
        # athena_dataupload_task.delay(
        #     request.user.id,
        #     workflow.id,
        #     conn.id,
        #     form.get_field_dict(),
        #     log_item.id)

        # Show log execution
        # return render(
        #     self.request,
        #     'dataops/operation_done.html',
        #     {'log_id': log_item.id, 'back_url': reverse('table:display')})

        return redirect('under_construction')
