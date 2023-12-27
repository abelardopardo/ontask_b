"""First step for Canvas Course Upload."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask.dataops.views import upload_steps
from ontask import models, OnTaskException
from ontask.core import canvas_ops, get_workflow, is_instructor, session_ops
from ontask.dataops import services, pandas


class CanvasUploadStart(upload_steps.UploadStepOneView):
    """Start the upload of information from Canvas. May need OAuth

    The different operations are defined by parameters used when invoking
    this as a view. See url.py in this module.
    """
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Needed for authentication purposes
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Check for the CANVAS token and proceed to the continue_url
        session_ops.set_payload(
            self.request,
            {
                'step_1': reverse(self.step_1_url),
                'target_url': form.cleaned_data['target_url'],
                'canvas_course_id': form.cleaned_data['canvas_course_id'],
                'upload_enrollment': form.cleaned_data['upload_enrollment'],
                'upload_quizzes': form.cleaned_data['upload_quizzes'],
                'upload_assignments': form.cleaned_data['upload_assignments'],
                'include_course_id_column': form.cleaned_data[
                    'include_course_id_column']})

        # Go fetch the OAuth token, callback is canvas_upload_start_finish
        return canvas_ops.set_oauth_token(
            self.request,
            form.cleaned_data['target_url'],
            'dataops:canvas_upload_start_finish',
            'dataops:uploadmerge')


@user_passes_test(is_instructor)
@get_workflow()
def canvas_upload_start_finish(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Callback return. Finish the processing of a canvas upload operation

    :param request: Http request (should be a post)
    :param workflow: Workflow object.
    :return: Load the data from Canvas and store it in the temporary DB
    """
    # Process Canvas API call to get the list of students
    payload = session_ops.get_payload(request)
    try:
        data_frame = services.create_df_from_canvas_course(
            request.user,
            payload.pop('target_url'),
            payload.pop('canvas_course_id'),
            payload.pop('upload_enrollment'),
            payload.pop('upload_quizzes'),
            payload.pop('upload_assignments'),
            payload.pop('include_course_id_column'))

        if data_frame.empty:
            raise OnTaskException(
                _('There are no students enrolled in the Canvas course.'))

        pandas.verify_data_frame(data_frame)

        frame_info = pandas.store_temporary_dataframe(data_frame, workflow)
    except Exception as exc:
        messages.error(
            request,
            _('Canvas upload was not successful: {0}').format(
                str(exc)))
        return redirect('dataops:uploadmerge')

    # Dictionary to populate gradually throughout the sequence of steps.
    # It is stored in the session.
    session_ops.set_payload(
        request,
        {
            'initial_column_names': frame_info[0],
            'column_types': frame_info[1],
            'src_is_key_column': frame_info[2],
            'step_1': reverse('dataops:canvas_course_upload_start'),
            'log_upload':
                models.Log.WORKFLOW_DATA_CANVAS_COURSE_UPLOAD})

    return redirect('dataops:upload_s2')
