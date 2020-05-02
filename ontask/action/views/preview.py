# -*- coding: utf-8 -*-

"""Views to preview resulting text in the action."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.action import services
from ontask.core import ajax_required, get_action, is_instructor


@csrf_exempt
@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def preview_next_all_false(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    idx: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Preview message with all conditions evaluating to false.

    Previews the message that has all conditions incorrect in the position
    next to the one specified by idx

    The function uses the list stored in rows_all_false and finds the next
    index in that list (or the first one if it is the last. It then invokes
    the preview_response method

    :param request: HTTP Request object
    :param pk: Primary key of the action
    :param idx: Index of the preview requested
    :param workflow: Current workflow being manipulated
    :param action: Action being used in preview (set by the decorators)
    :return: JSON Response with the rendering of the preview
    """
    del workflow
    # Get the list of indexes
    idx_list = action.rows_all_false

    if not idx_list:
        # If empty, or None, something went wrong.
        return http.JsonResponse({'html_redirect': reverse('home')})

    # Search for the next element bigger than idx
    next_idx = next((nxt for nxt in idx_list if nxt > idx), None)

    if not next_idx:
        # If nothing found, then take the first element
        next_idx = idx_list[0]

    # Return the rendering of the given element
    return preview_response(request, pk, idx=next_idx, action=action)


@csrf_exempt
@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def preview_response(
    request: http.HttpRequest,
    pk: int,
    idx: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Preview content of action.

    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param idx: Index of the reponse to preview
    :param workflow: Current workflow being manipulated
    :param action: Might have been fetched already
    :return: http.JsonResponse
    """
    del pk, workflow
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    # Initial context to render the response page.
    context = {'action': action, 'index': idx}
    if (
        action.action_type == models.Action.EMAIL_REPORT
        or action.action_type == models.Action.JSON_REPORT
    ):
        services.create_list_preview_context(action, context)
    else:
        services.create_row_preview_context(
            action,
            idx,
            context,
            request.GET.get('subject_content'))

    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_preview.html',
            context,
            request=request)})
