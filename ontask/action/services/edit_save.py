# -*- coding: utf-8 -*-

"""Service to save the action when editing."""

from typing import Optional, Union

from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse

from ontask import models
from ontask.action import forms


def save_action_form(
    request: HttpRequest,
    form: Union[forms.ActionForm, forms.ActionUpdateForm],
    template_name: str,
    workflow: Optional[models.Workflow] = None,
) -> JsonResponse:
    """Save information from the form to manipulate condition/filter.

    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.

    :param request: Request object

    :param form: Form to be used in the request/render

    :param template_name: Template for rendering the content

    :param workflow: workflow being processed.

    :return: JSON response
    """
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        if models.Action.TODO_LIST == form.cleaned_data.get('action_type'):
            # To be implemented
            return JsonResponse(
                {'html_redirect': reverse('under_construction')})

        # Fill in the fields of the action (without saving to DB)_
        action_item = form.save(commit=False)

        if action_item.pk is None:
            # Action is New. Update certain vars
            action_item.workflow = workflow
            action_item.save()
            log_type = models.Log.ACTION_CREATE
            return_url = reverse('action:edit', kwargs={'pk': action_item.id})
        else:
            action_item.save()
            log_type = models.Log.ACTION_UPDATE
            return_url = reverse('action:index')

        action_item.log(request.user, log_type)
        return JsonResponse({'html_redirect': return_url})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form},
            request=request),
    })
