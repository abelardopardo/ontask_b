# -*- coding: utf-8 -*-

"""Pages to edit the attributes."""

from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.forms import forms
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from action.models import Condition
from logs.models import Log
from ontask.decorators import get_workflow, ajax_required
from ontask.permissions import is_instructor
from workflow.forms import AttributeItemForm
from workflow.models import Workflow


def save_attribute_form(
    request: HttpRequest,
    workflow: Workflow,
    template: str,
    form: forms.Form,
    attr_idx: int
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

        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_ATTRIBUTE_CREATE,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name,
                'attr_key': form.cleaned_data['key'],
                'attr_val': form.cleaned_data['attr_value']})

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            template,
            {'form': form,
             'id': attr_idx},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_create(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Render the view to create an attribute."""
    form = AttributeItemForm(
        request.POST or None,
        keys=list(workflow.attributes.keys()),
        workflow=workflow,
    )

    return save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_create.html',
        form,
        -1)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Render the edit attribute page."""
    # Get the list of keys
    keys = sorted(workflow.attributes.keys())

    # Get the key/value pair
    key = keys[int(pk)]
    attr_value = workflow.attributes[key]

    # Remove the one being edited
    keys.remove(key)

    # Create the form object with the form_fields just computed
    form = AttributeItemForm(
        request.POST or None,
        key=key,
        value=attr_value,
        keys=keys,
        workflow=workflow)

    return save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_edit.html',
        form,
        int(pk))


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def attribute_delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Delete an attribute attached to the workflow.

    :param request: Request object

    :param pk: number of the attribute with respect to the sorted list of
    items.

    :return:
    """
    # Get the key
    wf_attributes = workflow.attributes
    key = sorted(wf_attributes.keys())[int(pk)]

    if request.method == 'POST':
        # Pop the attribute
        # Hack, the pk has to be divided by two because it names the elements
        # in itesm (key and value).
        attr_val = wf_attributes.pop(key, None)
        workflow.attributes = wf_attributes

        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_ATTRIBUTE_DELETE,
            workflow,
            {
                'id': workflow.id,
                'attr_key': key,
                'attr_val': attr_val,
            },
        )

        workflow.save()

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_attribute_delete.html',
            {'pk': pk, 'key': key},
            request=request),
    })
