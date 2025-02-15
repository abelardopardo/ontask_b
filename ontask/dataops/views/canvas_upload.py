"""First step for Canvas Course Enrollment upload."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models, OnTaskException
from ontask.core import (
    SessionPayload, canvas_ops, get_workflow, is_instructor, OnTaskDebug)
from ontask.dataops import services
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
        # Check for the CANVAS token and proceed to the continue_url
        self.request.session['upload_data'] = {
            'step_1': self.step_1_url,
            'log_upload': self.log_type,
            'target_url': form.cleaned_data['target_url'],
            'canvas_course_id': form.cleaned_data['canvas_course_id']}

        SessionPayload(
            self.request.session,
            initial_values={'target_url': form.cleaned_data['target_url']})

        return canvas_ops.get_or_set_oauth_token(
            self.request,
            form.cleaned_data['target_url'],
            'dataops:canvas_upload_start_finish',
            'dataops:uploadmerge')


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


@user_passes_test(is_instructor)
@get_workflow()
def canvas_upload_start_finish(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Finish the processing of a canvas upload operation

    :param request: Http request (should be a post)
    :param workflow: Workflow object.
    :return: Load the data from Canvas and store it in the temporary DB
    """
    # Process Canvas API call to get the list of students
    OnTaskDebug.set_trace('')
    try:
        op_type = request.session['upload_data'].get('log_upload')
        target_url = request.session['upload_data'].pop('target_url')
        course_id = request.session['upload_data'].pop('canvas_course_id')
        if (op_type ==
                models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD):
            OnTaskDebug.set_trace('')
            data_frame = services.create_df_from_canvas_course_enrollment(
                    request.user,
                    target_url,
                    course_id)
            OnTaskDebug.set_trace('')
        elif (op_type ==
              models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD):
            OnTaskDebug.set_trace('')
            data_frame = services.create_df_from_canvas_course_quizzes(
                request.user,
                target_url,
                course_id)
            OnTaskDebug.set_trace('')
        else:
            raise OnTaskException(
                _('Unexpected Canvas operation not supported.'))

        if data_frame.empty:
            raise OnTaskException(
                _('There are no students enrolled in the Canvas course.'))

        # Check validity of the data frame and store in temporary table in DB
        OnTaskDebug.set_trace('')
        frame_info = common.validate_and_store_temporary_data_frame(
            workflow,
            data_frame)

    except Exception as exc:
        messages.error(
            request,
            _('Canvas course upload could not be processed: {0}, {1}').format(
                getattr(exc, 'message', repr(exc)),
                OnTaskDebug.last_trace_message))
        OnTaskDebug.last_trace_message = ''
        return redirect('dataops:canvas_course_enrollments_upload_start')

    # Dictionary to populate gradually throughout the sequence of steps.
    # It is stored in the session.
    request.session['upload_data'].update({
        'initial_column_names': frame_info[0],
        'column_types': frame_info[1],
        'src_is_key_column': frame_info[2]})

    return redirect('dataops:upload_s2')
