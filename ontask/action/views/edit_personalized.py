# -*- coding: utf-8 -*-

"""Views to edit actions that send personalized information."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ontask import models
from ontask.action import forms
from ontask.core import ajax_required, get_action, get_view, is_instructor


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@get_action(pf_related='actions')
def save_text(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Save text content of the action.

    :param request: HTTP request (POST)
    :param pk: Action ID
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being saved (set by the decorators)
    :return: Nothing, changes reflected in the DB
    """
    del pk, workflow
    # Wrong type of action.
    if action.is_in:
        return http.JsonResponse({'html_redirect': reverse('home')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def showurl(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Create page to show URL to access action.

    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.

    :param request: Json request
    :param pk: Primary key of the action to show the URL
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being manipulated (set by the decorators)
    :return: Json response with the content to show in the screen
    """
    del pk, workflow
    form = forms.EnableURLForm(request.POST or None, instance=action)

    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            action.log(
                request.user,
                models.Log.ACTION_SERVE_TOGGLED,
                served_enabled=action.serve_enabled)

            return http.JsonResponse(
                {'html_redirect': reverse('action:index')})

        return http.JsonResponse({'html_redirect': None})

    # Render the page with the absolute URI
    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_showurl.html',
            {'url_text': request.build_absolute_uri(
                reverse('action:serve_lti') + '?id=' + str(action.id)),
             'form': form,
             'action': action},
            request=request),
    })


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_POST
@get_view()
def add_attachment(
    request: http.HttpRequest,
    pk: int,
    action_id: int,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Add a View to an Email Report action

    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.

    :param request: Json request
    :param pk: Primary key of the view to attach to the action
    :param action_id: Action being manipulated
    :param workflow: Workflow being manipulated (set by the decorators)
    :param view: View object to be attached to the action
    :return: Json response that prompts refresh after operation
    """
    del pk
    # Get the action
    action = workflow.actions.filter(pk=action_id).first()
    if not action or action.action_type != models.Action.EMAIL_REPORT:
        return http.JsonResponse({'html_rediret': reverse('action:index')})

    # If the request has 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    action.attachments.add(view)
    action.save()

    # Refresh the page to show the column in the list.
    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_POST
@get_view()
def remove_attachment(
    request: http.HttpRequest,
    pk: int,
    action_id: int,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Remove a view from an Email Report action

    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.

    :param request: Json request
    :param pk: Primary key of the view to attach to the action
    :param action_id: Action being manipulated
    :param workflow: Workflow being manipulated (set by the decorators)
    :param view: View object to be attached to the action
    :return: Json response that prompts refresh after operation
    """
    del pk
    # Get the action
    action = workflow.actions.filter(pk=action_id).first()
    if not action or action.action_type != models.Action.EMAIL_REPORT:
        return http.JsonResponse({'html_rediret': reverse('action:index')})

    # If the request has 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    action.attachments.remove(view)
    action.save()

    # Refresh the page to show the column in the list.
    return http.JsonResponse({'html_redirect': ''})
