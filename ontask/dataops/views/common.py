# -*- coding: utf-8 -*-

"""Common classes to upload data."""
from django.urls import reverse

from ontask.core import UserIsInstructor, WorkflowView


class UploadStart(UserIsInstructor, WorkflowView):
    dtype = None
    dtype_select = None
    prev_step_url = 'dataops:uploadmerge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'dtype': self.dtype,
            'dtype_select': self.dtype_select,
            'value_range': range(5) if self.workflow.has_table() else range (3),
            'prev_step': reverse(self.prev_step_url)})
        return context
