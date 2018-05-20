# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

import logs.ops
from action.models import Condition
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from .forms import (AttributeItemForm)
from .ops import (get_workflow)


class AttributeTable(tables.Table):
    """
    Table to render the list of attributes attached to a workflow
    """
    name = tables.Column(verbose_name=str('Name'))
    value = tables.Column(verbose_name=str('Value'))
    operations = OperationsColumn(
        verbose_name='Ops',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id'], }
    )

    class Meta:
        fields = ('name', 'value', 'operations')
        attrs = {
            'class': 'table display table-bordered',
            'id': 'attribute-table'
        }


@user_passes_test(is_instructor)
def attributes(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    attribute_data = [
        {'id': idx, 'name': k, 'value': v}
        for idx, (k, v) in enumerate(sorted(workflow.attributes.items()))]

    # Context to render the template
    context = {
        'table': AttributeTable(attribute_data, orderable=False),
        'wid': workflow.id
    }

    return render(request, 'workflow/attributes.html', context)


def save_attribute_form(request, workflow, template, form, key_idx):
    """
    Function to process the AJAX request to create or update an attribute
    :param request: Request object received
    :param workflow: current workflow being manipulated
    :param form: Form used to ask for data
    :return: AJAX reponse
    """

    # Ajax response. Form is not valid until proven otherwise
    data = {'form_is_valid': False}

    if request.method != 'POST' or not form.is_valid():
        data['html_form'] = render_to_string(
            template,
            {'form': form,
             'id': key_idx},
            request=request)

        return JsonResponse(data)

    # Correct form submitted

    # Enforce the property that Attribute names, column names and
    # condition names cannot overlap.
    attr_name = form.cleaned_data['key']
    if attr_name in workflow.get_column_names():
        form.add_error(
            'key',
            'There is a column with this name. Please change.'
        )
        data['html_form'] = render_to_string(
            template,
            {'form': form,
             'id': key_idx},
            request=request)

        return JsonResponse(data)

    # Check if there is a condition with that name
    cond_names = Condition.objects.filter(
        action__workflow=workflow
    ).values_list('name', flat=True)
    if attr_name in cond_names:
        form.add_error(
            'key',
            'There is a condition already with this name.'
        )
        data['html_form'] = render_to_string(
            'workflow/includes/partial_attribute_create.html',
            {'form': form,
             'id': key_idx},
            request=request)

        return JsonResponse(data)

    # proceed with updating the attributes.
    wf_attributes = workflow.attributes

    # If key_idx is not -1, this means we are editing an existing pair
    if key_idx != -1:
        key = sorted(wf_attributes.keys())[key_idx]
        wf_attributes.pop(key)

    # Update value
    wf_attributes[form.cleaned_data['key']] = form.cleaned_data['value']

    workflow.attributes = wf_attributes
    workflow.save()

    # Log the event
    logs.ops.put(request.user,
                 'workflow_attribute_create',
                 workflow,
                 {'id': workflow.id,
                  'name': workflow.name,
                  'attr_key': form.cleaned_data['key'],
                  'attr_val': form.cleaned_data['value']})

    data['form_is_valid'] = True
    data['html_redirect'] = reverse('workflow:attributes')
    return JsonResponse(data)


@user_passes_test(is_instructor)
def attribute_create(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Create the form object with the form_fields just computed
    form = AttributeItemForm(request.POST or None,
                             keys=workflow.attributes.keys())

    return save_attribute_form(
        request,
        workflow,
        'workflow/includes/partial_attribute_create.html',
        form,
        -1)


@user_passes_test(is_instructor)
def attribute_edit(request, pk):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

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
def attribute_delete(request, pk):
    """
    Request to delete an attribute attached to the workflow
    :param request: Request object
    :param pk: number of the attribute with respect to the sorted list of items.
    :return:
    """
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # JSON answer
    data = dict()
    data['form_is_valid'] = False

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
        logs.ops.put(request.user,
                     'workflow_attribute_delete',
                     workflow,
                     {'id': workflow.id,
                      'attr_key': key,
                      'attr_val': val})

        workflow.save()

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:attributes')

    data['html_form'] = render_to_string(
        'workflow/includes/partial_attribute_delete.html',
        {'pk': pk, 'key': key},
        request=request)

    return JsonResponse(data)
