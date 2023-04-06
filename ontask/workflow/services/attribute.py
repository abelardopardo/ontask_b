"""Pages to manipulate attributes."""
from typing import Optional

from django import http
from django.forms import forms

from ontask import models


def save_attribute_form(
    request: http.HttpRequest,
    form: forms.Form,
    attr_idx: Optional[int] = None,
) -> http.JsonResponse:
    """Process the AJAX request to create or update an attribute.

    :param request: Request object received
    :param form: Form used to ask for data
    :param attr_idx: Index of the attribute being manipulated
    :return: AJAX response
    """
    if not form.has_changed():
        return http.JsonResponse({'html_redirect': ''})

    workflow = form.workflow
    # proceed with updating the attributes.
    wf_attributes = workflow.attributes

    # If key_idx is not None, this means we are editing an existing pair
    if attr_idx is not None:
        key = sorted(wf_attributes.keys())[attr_idx]
        wf_attributes.pop(key)

        # Rename the appearances of the variable in all actions
        for action_item in workflow.actions.all():
            action_item.rename_variable(key, form.cleaned_data['key'])

    # Update value
    wf_attributes[form.cleaned_data['key']] = form.cleaned_data[
        'attr_value']
    workflow.attributes = wf_attributes
    workflow.save(update_fields=['attributes'])
    workflow.log(
        request.user,
        models.Log.WORKFLOW_ATTRIBUTE_CREATE,
        **wf_attributes)
    return http.JsonResponse({'html_redirect': ''})
