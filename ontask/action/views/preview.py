# -*- coding: utf-8 -*-

"""Views to preview resulting text in the action."""

from django import http
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator

from ontask import models
from ontask.action import services
from ontask.core import (
    ActionView, JSONFormResponseMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ActionPreviewView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Preview action content.

    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.
    """

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs) -> http.JsonResponse:
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) -> http.JsonResponse:
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)

        # Initial context to render the response page.
        idx = kwargs.get('idx')
        context = {'action': self.action, 'index': idx}
        if (
            self.action.action_type == models.Action.EMAIL_REPORT
            or self.action.action_type == models.Action.JSON_REPORT
        ):
            services.create_list_preview_context(self.action, context)
        else:
            services.create_row_preview_context(
                self.action,
                idx,
                context,
                request.GET.get('subject_content'))

        return http.JsonResponse({
            'html_form': render_to_string(
                'action/includes/partial_preview.html',
                context,
                request=request)})


@method_decorator(ajax_required, name='dispatch')
class ActionPreviewNextAllFalseView(ActionPreviewView):
    """Preview message with all conditions evaluating to false.

    Previews the message that has all conditions incorrect in the position
    next to the one specified by idx

    The function uses the list stored in rows_all_false and finds the next
    index in that list (or the first one if it is the last. It then invokes
    the preview_response method.
    """

    def post(self, request, *args, **kwargs) -> http.JsonResponse:
        # Get the list of indexes
        idx_list = self.action.rows_all_false

        if not idx_list:
            # If empty, or None, something went wrong.
            return http.JsonResponse({'html_redirect': reverse('home')})

        # Search for the next element bigger than idx
        next_idx = next(
            (nxt for nxt in idx_list if nxt > self.kwargs.get('idx')),
            idx_list[0])

        # Return the rendering of the given element
        return super().post(request, idx=next_idx)
