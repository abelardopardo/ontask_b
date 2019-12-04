# -*- coding: utf-8 -*-

"""Views to render the list of actions."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import models
from ontask.action import services
from ontask.action.forms import ActionForm, ActionUpdateForm
from ontask.core import SessionPayload
from ontask.core.decorators import ajax_required, get_action, get_workflow
from ontask.core.permissions import UserIsInstructor, is_instructor


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_index(
    request: http.HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    del wid
    """Show all the actions attached to the workflow.

    :param request: HTTP Request
    :param wid: Primary key of the workflow object to use
    :param workflow: Workflow for the session.
    :return: HTTP response
    """
    # Reset object to carry action info throughout dialogs
    SessionPayload.flush(request.session)
    return render(
        request,
        'action/index.html',
        {
            'workflow': workflow,
            'table': services.ActionTable(
                workflow.actions.all(),
                orderable=False)})


class ActionCreateView(UserIsInstructor, generic.TemplateView):
    """Process get/post requests to create an action."""

    form_class = ActionForm

    template_name = 'action/includes/partial_action_create.html'

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def get(
        self,
        request: http.HttpRequest,
        *args, **kwargs
    ) -> http.HttpResponse:
        """Process the get requet when creating an action."""
        return services.save_action_form(
            request,
            self.form_class(workflow=kwargs.get('workflow')),
            self.template_name,
            workflow=kwargs.get('workflow'),
        )

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def post(self, request: http.HttpRequest, **kwargs) -> http.HttpResponse:
        """Process the post request when creating an action."""
        return services.save_action_form(
            request,
            self.form_class(request.POST, workflow=kwargs.get('workflow')),
            self.template_name,
            workflow=kwargs.get('workflow'),
        )


class ActionUpdateView(UserIsInstructor, generic.DetailView):
    """Process the Action Update view.

    @DynamicAttrs
    """

    model = models.Action
    template_name = 'action/includes/partial_action_update.html'
    context_object_name = 'action'
    form_class = ActionUpdateForm

    def get_object(self, queryset=None) -> models.Action:
        """Access the Action object being manipulated."""
        act_obj = super().get_object(queryset=queryset)
        if act_obj.workflow.id != self.request.session['ontask_workflow_id']:
            raise http.Http404()

        return act_obj

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def get(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs
    ) -> http.HttpResponse:
        """Process the get request."""
        return services.save_action_form(
            request,
            self.form_class(
                instance=self.get_object(),
                workflow=kwargs['workflow']),
            self.template_name)

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def post(self, request: http.HttpRequest, **kwargs) -> http.HttpResponse:
        """Process post request."""
        return services.save_action_form(
            request,
            self.form_class(
                request.POST,
                instance=self.get_object(),
                workflow=kwargs['workflow'],
            ),
            self.template_name)


@user_passes_test(is_instructor)
@get_action(pf_related=['actions', 'columns'])
def edit_action(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.HttpResponse:
    """Invoke the specific edit view.

    :param request: Request object
    :param pk: Action PK
    :param workflow: Workflow being processed,
    :param action: Action being edited (set by the decorator)
    :return: HTML response
    """
    del pk
    return services.action_process_factory.process_edit_request(
        request,
        workflow,
        action)


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def delete_action(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Process AJAX request to delete an action.

    :param request: Request object
    :param pk: Action id to delete.
    :param workflow: Workflow being processed,
    :param action: Action being deleted (set by the decorator)
    :return: JSON Response
    """
    del pk, workflow
    # JSON response object
    # Get the appropriate action object
    if request.method == 'POST':
        action.log(request.user, models.Log.ACTION_DELETE)
        action.delete()
        return http.JsonResponse({'html_redirect': reverse('action:index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_delete.html',
            {'action': action},
            request=request),
    })
