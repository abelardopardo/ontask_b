# -*- coding: utf-8 -*-

"""Service to save the action when editing."""
import copy
from typing import Optional, Union

from django import http
from django.template.loader import render_to_string
from django.urls import reverse

from ontask import models
from ontask.action import forms


def save_action_form(
    request: http.HttpRequest,
    form: Union[forms.ActionForm, forms.ActionUpdateForm],
    template_name: str,
    view_as_filter: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Save information from the form to manipulate condition/filter.

    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.

    :param request: Request object
    :param form: Form to be used in the request/render
    :param template_name: Template for rendering the content
    :param view_as_filter: Id of optional view to use as filter
    :param workflow: workflow being processed.
    :return: JSON response
    """
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        # Fill in the fields of the action (without saving to DB)_
        action_item = form.save(commit=False)

        if action_item.pk is None:
            # Action is New. Update certain vars
            action_item.workflow = workflow
            action_item.save()

            if view_as_filter is not None:
                view = workflow.views.filter(pk=view_as_filter).first()
                if view is None:
                    return http.JsonResponse({'html_redirect': None})

                view.filter.action = action_item

            log_type = models.Log.ACTION_CREATE
            return_url = reverse('action:edit', kwargs={'pk': action_item.id})
        else:
            action_item.save()
            log_type = models.Log.ACTION_UPDATE
            return_url = reverse('action:index')

        action_item.log(request.user, log_type)
        return http.JsonResponse({'html_redirect': return_url})

    form_url = reverse('action:create')
    if view_as_filter is not None:
        form_url = reverse(
            'action:create_from_view',
            kwargs={'fid': view_as_filter})

    return http.JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'form_url': form_url},
            request=request),
    })
