"""Function to upload a data frame from an Athena connection object."""

from django.shortcuts import redirect
from django.views import generic

from ontask.dataops.views import upload_steps
from ontask import models


class AthenaUploadStart(upload_steps.UploadStepOneView, generic.UpdateView):
    """Start the upload of a data frame through an Athena connection.

    The parameters are obtained and if valid, an operation is scheduled for
    execution.
    """

    def get_queryset(self):
        """This view should only consider enabled connections."""
        return self.model.objects.filter(enabled=True)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        self.workflow.log(
            self.request.user,
            models.Log.WORKFLOW_DATA_ATHENA_UPLOAD,
            connection=self.object.name,
            status='Preparing to execute')

        # Batch execution -- UNDER CONSTRUCTION
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
