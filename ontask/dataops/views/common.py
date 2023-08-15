"""Common classes to upload data."""
from django.urls import reverse

from ontask.core import UserIsInstructor, WorkflowView


class UploadStart(UserIsInstructor, WorkflowView):
    data_type = None
    data_type_select = None
    prev_step_url = 'dataops:uploadmerge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'data_type': self.data_type,
            'data_type_select': self.data_type_select,
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'prev_step': reverse(self.prev_step_url)})
        return context
