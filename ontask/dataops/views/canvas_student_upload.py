"""First step for Canvas Course Enrollment upload."""
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from ontask.dataops.views import common


class CanvasUploadStart(common.UploadStart, generic.FormView):
    """Start the upload of information from Canvas.

    The different operations are defined by parameters used when invoking
    this as a view. See url.py in this module.
    """

    # To be defined in subclasses
    log_type = None
    step_1_url = None

    def get_context_data(self, **kwargs):
        """Store the attribute with a canvas course id if it exists"""
        context = super().get_context_data()
        if 'CANVAS COURSE ID' in self.workflow.attributes:
            # Page should not show form, and instead a confirmation page
            context['confirm_canvas_course_id'] = self.workflow.attributes[
                'CANVAS COURSE ID']
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        # Needed for authentication purposes
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Dictionary to populate gradually throughout the sequence of steps.
        # It is stored in the session.
        self.request.session['upload_data'] = {
            'initial_column_names': form.frame_info[0],
            'column_types': form.frame_info[1],
            'src_is_key_column': form.frame_info[2],
            'step_1': self.step_1_url,
            'log_upload': self.log_type}

        return redirect('dataops:upload_s2')


class CanvasCourseEnrollmentsUploadStart(CanvasUploadStart):
    """Step 1 URL needs to be defined at instantiation time."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_1_url = reverse(
            'dataops:canvas_course_enrollments_upload_start')


class CanvasCourseQuizzesUploadStart(CanvasUploadStart):
    """Step 1 URL needs to be defined at instantiation time."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_1_url = reverse('dataops:canvas_course_quizzes_upload_start')
