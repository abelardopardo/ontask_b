"""Service to save the action when editing."""
from typing import Optional

from django import http

from ontask import models


def save_action_form(
    action: models.Action,
    user,
    log_type: str,
    return_url: str,
    view_as_filter: Optional[int] = None,
) -> http.JsonResponse:
    """Save action object.

    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.

    :param action: action object being saved
    :param user: User that submitted the request
    :param log_type: Type of log message to create
    :param return_url: URL to use as success POST
    :param view_as_filter: Filter ID if action is created from View
    :return: JSON response
    """

    if view_as_filter is not None:
        if (view := action.workflow.views.filter(
                pk=view_as_filter).first()) is None:
            return http.JsonResponse({'html_redirect': None})

        action.filter = view.filter
        action.save()

    action.log(user, log_type)
    return http.JsonResponse({'html_redirect': return_url})
