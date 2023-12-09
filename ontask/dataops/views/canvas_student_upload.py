"""First step for Canvas Course Student upload."""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.dataops.views import common


class CanvasCourseStudentUploadStart(common.UploadStart, generic.FormView):
    """Start the upload of student listing in a Canvas course.

    The four-step process will populate the dictionary with name upload_data.

    STEP 1:

    initial_column_names: id, student name

    column_types: int (student id), str (student name)

    src_is_key_column: [True, False],

    step 1: URL name of the first step."""

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
            'step_1': reverse('dataops:canvas_course_students_upload_start'),
            'log_upload':
                models.Log.WORKFLOW_DATA_CANVAS_COURSE_STUDENT_UPLOAD}

        return redirect('dataops:upload_s2')
