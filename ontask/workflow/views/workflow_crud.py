# -*- coding: utf-8 -*-

"""Views implementing CRUD operations with workflows."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.celery import celery_is_up
from ontask.core import (
    UserIsInstructor, ajax_required, get_workflow, is_instructor,
    remove_workflow_from_session,
)
from ontask.workflow import forms, services


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    """View to create a workflow."""

    form_class = forms.WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

    @method_decorator(ajax_required)
    def get(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs,
    ) -> http.JsonResponse:
        """Process the get request."""
        return http.JsonResponse({
            'html_form': render_to_string(
                self.template_name,
                {'form': self.form_class(workflow_user=request.user)},
                request=request)})

    @method_decorator(ajax_required)
    def post(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs,
    ) -> http.JsonResponse:
        """Process the post request."""
        del args, kwargs
        form = self.form_class(request.POST, workflow_user=request.user)
        if request.method == 'POST' and form.is_valid():
            if not form.has_changed():
                return http.JsonResponse({'html_redirect': None})

            return services.save_workflow_form(request, form)

        return http.JsonResponse({
            'html_form': render_to_string(
                self.template_name,
                {'form': form},
                request=request)})


@user_passes_test(is_instructor)
def index(request: http.HttpRequest) -> http.HttpResponse:
    """Render the page with the list of workflows.

    :param request: HttpRequest received
    :return: Response with the index page rendered
    """
    remove_workflow_from_session(request)

    # Report if Celery is not running properly
    if request.user.is_superuser:
        # Verify that celery is running!
        if not celery_is_up():
            messages.error(
                request,
                _(
                    'WARNING: Celery is not currently running. '
                    + 'Please configure it correctly.',
                ),
            )

    return render(
        request,
        'workflow/index.html',
        services.get_index_context(request.user))


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def update(
    request: http.HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Update the workflow information (name, description).

    :param request: Request object
    :param wid: Workflow ID
    :param workflow: workflow being manipulated.
    :return: JSON response
    """
    if workflow.user != request.user:
        # If the user does not own the workflow, notify error and go back to
        # index
        messages.error(
            request,
            _('You can only rename workflows you created.'))
        return http.JsonResponse({'html_redirect': ''})

    form = forms.WorkflowForm(
        request.POST or None,
        instance=workflow,
        workflow_user=workflow.user)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_workflow_form(request, form)

    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_update.html',
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def delete(
    request: http.HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Delete a workflow.

    :param request: Http Request
    :param wid: Primary key for the workflow
    :param workflow: workflow object being manipulated
    :return: JSON page with the delete form
    """
    if request.method == 'POST':
        workflow.log(request.user, models.Log.WORKFLOW_DELETE)
        workflow.delete()
        return http.JsonResponse({'html_redirect': reverse('home')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_delete.html',
            {'workflow': workflow},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def clone_workflow(
    request: http.HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Clone a workflow.

    :param request: HTTP request
    :param wid: Workflow id
    :param workflow: Workflow being cloned
    :return: JSON data
    """
    # Get the current workflow
    # Initial data in the context
    context = {'pk': wid, 'name': workflow.name}

    if request.method == 'GET':
        return http.JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_workflow_clone.html',
                context,
                request=request),
        })

    try:
        services.do_clone_workflow(request.user, workflow)
    except OnTaskServiceException as exc:
        exc.message_to_error(request)
        exc.delete()
        return http.JsonResponse({'html_redirect': ''})

    messages.success(
        request,
        _('Workflow successfully cloned.'))
    return http.JsonResponse({'html_redirect': ''})
