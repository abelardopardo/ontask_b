# -*- coding: utf-8 -*-

"""Pages to manipulate attributes."""
from django.forms import forms
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template.loader import render_to_string

from ontask import models


def save_attribute_form(
    request: HttpRequest,
    workflow: models.Workflow,
    template: str,
    form: forms.Form,
    attr_idx: int,
) -> JsonResponse:
    """Process the AJAX request to create or update an attribute.

    :param request: Request object received
    :param workflow: current workflow being manipulated
    :param template: Template to render in the response
    :param form: Form used to ask for data
    :param attr_idx: Index of the attribute being manipulated
    :return: AJAX reponse
    """
    if request.method == 'POST' and form.is_valid():
        # Correct form submitted
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        # proceed with updating the attributes.
        wf_attributes = workflow.attributes

        # If key_idx is not -1, this means we are editing an existing pair
        if attr_idx != -1:
            key = sorted(wf_attributes.keys())[attr_idx]
            wf_attributes.pop(key)

            # Rename the appearances of the variable in all actions
            for action_item in workflow.actions.all():
                action_item.rename_variable(key, form.cleaned_data['key'])

        # Update value
        wf_attributes[form.cleaned_data['key']] = form.cleaned_data[
            'attr_value']
        workflow.attributes = wf_attributes
        workflow.save()
        workflow.log(
            request.user,
            models.Log.WORKFLOW_ATTRIBUTE_CREATE,
            **wf_attributes)
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            template,
            {'form': form,
             'id': attr_idx},
            request=request),
    })
