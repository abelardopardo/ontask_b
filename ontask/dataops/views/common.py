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
        context['dtype'] = self.dtype
        context['dtype_select'] = self.dtype_select
        if self.workflow.has_table():
            context['value_range'] = range(5)
        else:
            context['value_range'] = range(3)
        context['prev_step'] = reverse(self.prev_step_url)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs
