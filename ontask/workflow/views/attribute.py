# -*- coding: utf-8 -*-

"""Pages to edit the attributes."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string

from ontask import models
from ontask.core import ajax_required, get_workflow, is_instructor
from ontask.workflow import forms, services


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_create(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Render the view to create an attribute.

    :param request: Http request received
    :param workflow: Workflow being processed
    :return: HttpResponse
    """
    return services.save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_create.html',
        forms.AttributeItemForm(
            request.POST or None,
            keys=list(workflow.attributes.keys()),
            workflow=workflow,
        ),
        -1)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_edit(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Render the view to edit an attribute.

    :param request: Http request received
    :param pk: Primery key of the attribute
    :param workflow: Workflow being processed
    :return: HttpResponse
    """
    # Get the list of keys
    keys = sorted(workflow.attributes.keys())

    # Get the key/value pair
    key = keys[int(pk)]
    attr_value = workflow.attributes[key]

    # Remove the one being edited
    keys.remove(key)

    return services.save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_edit.html',
        forms.AttributeItemForm(
            request.POST or None,
            key=key,
            value=attr_value,
            keys=keys,
            workflow=workflow),
        int(pk))


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_delete(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Delete an attribute attached to the workflow.

    :param request: Request object
    :param pk: number of the attribute with respect to the sorted list of
    items.
    :param workflow: Workflow being processed
    :return: JSON REsponse
    """
    wf_attributes = workflow.attributes
    key = sorted(wf_attributes.keys())[int(pk)]

    if request.method == 'POST':
        wf_attributes.pop(key, None)
        workflow.attributes = wf_attributes
        workflow.log(
            request.user,
            models.Log.WORKFLOW_ATTRIBUTE_DELETE,
            **wf_attributes)
        workflow.save()
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_attribute_delete.html',
            {'pk': pk, 'key': key},
            request=request),
    })
