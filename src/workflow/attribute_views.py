# -*- coding: utf-8 -*-
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from action.models import Condition
from logs.models import Log
from ontask.decorators import access_workflow, get_workflow
from ontask.permissions import is_instructor
from workflow.models import Workflow
from .forms import (AttributeItemForm)


def save_attribute_form(request, workflow, template, form, attr_idx):
    """Process the AJAX request to create or update an attribute.

    :param request: Request object received

    :param workflow: current workflow being manipulated

    :param template: Template to render in the response

    :param form: Form used to ask for data

    :param attr_idx: Index of the attribute being manipulated

    :return: AJAX reponse
    """
    if request.method != 'POST' or not form.is_valid():
        return JsonResponse({
            'html_form': render_to_string(
                template,
                {'form': form,
                 'id': attr_idx},
                request=request),
        })

    # Correct form submitted

    # Enforce the property that Attribute names, column names and
    # condition names cannot overlap.
    attr_name = form.cleaned_data['key']
    if attr_name in workflow.get_column_names():
        form.add_error(
            'key',
            _('There is a column with this name. Please change.')
        )
        return JsonResponse({
            'html_form': render_to_string(
                template,
                {'form': form,
                 'id': attr_idx},
                request=request)
        })

    # Check if there is a condition with that name
    cond_name = Condition.objects.filter(
        action__workflow=workflow,
        name=attr_name
    ).first()
    if cond_name:
        form.add_error(
            'key',
            _('There is a condition already with this name.')
        )
        return JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_attribute_create.html',
                {'form': form,
                 'id': attr_idx},
                request=request)
        })

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
    wf_attributes[form.cleaned_data['key']] = form.cleaned_data['value']

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
            'attr_val': form.cleaned_data['value']})

    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@get_workflow()
def attribute_create(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    # Get the workflow
    # Create the form object with the form_fields just computed
    form = AttributeItemForm(request.POST or None,
                             keys=list(workflow.attributes.keys()))

    return save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_create.html',
        form,
        -1)


@user_passes_test(is_instructor)
def attribute_edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    # Get the list of keys
    keys = sorted(workflow.attributes.keys())

    # Get the key/value pair
    key = keys[int(pk)]
    value = workflow.attributes[key]

    # Remove the one being edited
    keys.remove(key)

    # Create the form object with the form_fields just computed
    form = AttributeItemForm(request.POST or None,
                             key=key,
                             value=value,
                             keys=keys)

    return save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_edit.html',
        form,
        int(pk))


@user_passes_test(is_instructor)
@get_workflow()
def attribute_delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:

    """Delete an attribute attached to the workflow.

    :param request: Request object

    :param pk: number of the attribute with respect to the sorted list of items.

    :return:
    """
    # Get the key
    wf_attributes = workflow.attributes
    key = sorted(wf_attributes.keys())[int(pk)]

    if request.method == 'POST':
        # Pop the attribute
        # Hack, the pk has to be divided by two because it names the elements
        # in itesm (key and value).
        val = wf_attributes.pop(key, None)
        workflow.attributes = wf_attributes

        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_ATTRIBUTE_DELETE,
            workflow,
            {
                'id': workflow.id,
                'attr_key': key,
                'attr_val': val,
            },
        )

        workflow.save()

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_attribute_delete.html',
            {'pk': pk, 'key': key},
            request=request)
    })
