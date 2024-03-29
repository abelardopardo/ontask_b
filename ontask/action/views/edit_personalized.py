"""Views to edit actions that send personalized information."""
from typing import Dict

from django import http
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.action import forms
from ontask.core import (
    ActionView, JSONFormResponseMixin, UserIsInstructor,
    ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ActionShowURLView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.UpdateView,
):
    """Create page to show the URL to access an action.

    Given a JSON request with an action pk returns the URL used to retrieve
    the personalised message.
    """

    http_method_names = ['get', 'post']
    form_class = forms.EnableURLForm
    template_name = 'action/includes/partial_action_show_url.html'

    def get_context_data(self, **kwargs) -> Dict:
        """Get context data: The absolute URL for this action."""
        context = super().get_context_data(**kwargs)
        context['url_text'] = self.request.build_absolute_uri(
            reverse('action:serve_lti') + '?pk=' + str(self.object.id))
        return context

    def form_valid(self, form) -> http.JsonResponse:
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            self.object.log(
                self.request.user,
                models.Log.ACTION_SERVE_TOGGLED,
                served_enabled=self.object.serve_enabled)

            return http.JsonResponse(
                {'html_redirect': reverse('action:index')})

        return http.JsonResponse({'html_redirect': None})


@method_decorator(ajax_required, name='dispatch')
class ActionAddRemoveAttachmentView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Add a View to an Email Report action

    Given a JSON POST request with action and view pk updates the attachment
    field in the action.
    """
    http_method_names = ['post']
    is_add_operation = False
    pf_related = 'attachments'

    def post(self, request, *args, **kwargs) -> http.JsonResponse:
        # Get the view
        self.object = self.get_object()
        view = self.workflow.views.filter(pk=kwargs['view_id']).first()
        if not view or self.object.action_type != models.Action.EMAIL_REPORT:
            # View is not there, or does not point to the action or points to
            # the wrong action.
            return http.JsonResponse(
                {'html_redirect': reverse('action:index')})

        # If the request has 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.object.set_text_content(action_content)

        if self.is_add_operation:
            messages.success(request, _('Attachment {0} added.').format(
                view.name))
            self.object.attachments.add(view)
        else:
            messages.success(request, _('Attachment removed.'))
            self.object.attachments.remove(view)

        self.object.save()

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})
