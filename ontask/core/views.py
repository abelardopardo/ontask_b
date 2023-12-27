"""Basic views to render error."""
from django import http
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ontask import models
from ontask.tasks.execute import execute_operation
from ontask.core.decorators import ajax_required
from ontask.core.permissions import UserIsInstructor, is_admin, is_instructor
from ontask.core.services import ontask_handler404
from ontask.core import session_ops
from ontask.django_auth_lti.decorators import lti_role_required
from ontask.workflow.views import WorkflowIndexView


class ToBeDone(UserIsInstructor, generic.TemplateView):
    """Page showing the to be done."""

    template_name = 'base.html'


class HomeView(generic.View):
    """Render the home page."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        # Remove the payload dictionary from the session
        session_ops.flush_payload(request)
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))

        if is_instructor(request.user) or is_admin(request.user):
            return WorkflowIndexView.as_view()(request)

        # Authenticated request from learner, show profile
        return redirect(reverse('profiles:show_self'))


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
@method_decorator(
    lti_role_required(['Instructor', 'Learner']),
    name='dispatch')
class LTIEntryView(generic.RedirectView):
    """Response through LTI entry."""

    url = 'home'


class TrackView(generic.View):
    """Receive a request with a token from email read tracking.

    No permissions in this URL as it is supposed to be wide open to track email
    reads.
    """

    http_method_names = ['get']

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        # Push the tracking to the asynchronous queue
        execute_operation.delay(
            operation_type=models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
            payload={'method': request.method, 'get_dict': request.GET})

        return http.HttpResponse(status=200)


@method_decorator(ajax_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class KeepAliveView(generic.View):
    """Return empty response to keep session alive."""

    http_method_names = ['post']

    def post(self, request) -> http.HttpResponse:
        return http.JsonResponse({})


class Custom404View(generic.TemplateView):
    """Render the home page."""

    def get(self, request, *args, **kwargs):
        return ontask_handler404(request, Exception('Exception text'))
