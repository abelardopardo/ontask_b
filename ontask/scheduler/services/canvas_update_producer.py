"""Service functions to handle Canvas course uploads."""

from django import http
from django.utils.translation import gettext

from ontask import models
from ontask.core import canvas_ops, session_ops
from ontask.scheduler import forms
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)


class ScheduledOperationUpdateCanvasUpload(ScheduledOperationUpdateBaseView):
    """Class to create a Canvas Upload operation."""

    operation_type = None
    form_page_title = None
    form_class = forms.ScheduleUploadCanvasForm

    def _create_payload(
        self,
        request: http.HttpRequest,
        **kwargs
    ) -> dict:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param kwargs: Dictionary with extra parameters
        :return: Dictionary with pairs name/value
        """
        payload = super()._create_payload(request, **kwargs)

        payload.update({
            'workflow_id': self.workflow.id,
            'page_title': self.form_page_title})

        if self.object:
            payload['target_url'] = self.object.payload['target_url']
        else:
            payload['target_url'] = None

        return payload

    def form_valid(self, form) -> http.HttpResponse:
        """Process the valid POST request and insert Canvas Auth."""
        # Check for the CANVAS token and proceed to the continue_url
        session_ops.set_payload(self.request, self.op_payload)

        return canvas_ops.set_oauth_token(
            self.request,
            self.op_payload['target_url'],
            'scheduler:finish_scheduling',
            'scheduler:index')


class ScheduledOperationUpdateCanvasCourseEnrollmentUpload(
        ScheduledOperationUpdateCanvasUpload):
    """Class to CRUD a Canvas Course Enrollment Upload operation."""
    operation_type = models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD
    form_page_title = gettext('Canvas Course Enrollment Data Upload')


class ScheduledOperationUpdateCanvasCourseQuizzesUpload(
        ScheduledOperationUpdateCanvasUpload):
    """Class to CRUD a Canvas Course Quizzes Upload operation."""

    # Override form_class because it requires the column selection widget
    form_class = forms.ScheduleUploadCanvasQuizForm

    operation_type = models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD
    form_page_title = gettext('Canvas Course Quizzes Data Upload')
