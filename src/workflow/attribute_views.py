# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

import logs.ops
from action.models import Condition
from ontask.permissions import is_instructor
from .forms import (AttributeForm,
                    AttributeItemForm)
from .ops import (get_workflow)


@user_passes_test(is_instructor)
def attributes(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    wf_attributes = workflow.attributes
    # Get the form fields from the attributes and the current values
    form_fields = [(x, x + '__value', y)
                   for x, y in sorted(wf_attributes.items())]

    # Create the form object with the form_fields just computed
    form = AttributeForm(request.POST or None, form_fields=form_fields)

    if request.method == 'POST':
        if form.is_valid():
            # Check that the attribute names are different from column and
            # condition names.
            old_keys = wf_attributes.keys()
            condition_names = [x.name
                               for x in Condition.objects.filter(
                                action__workflow=workflow,
                                is_filter=False)]

            # Loop over all the keys in the form
            column_names = workflow.get_column_names()
            for old_key in old_keys:
                # Get the new proposed key to check
                new_key = form.cleaned_data[old_key]
                # Check #1: new key is not a column name
                if new_key in column_names:
                    # Attribute name collides with column!
                    form.add_error(
                        old_key,
                        'There is a column with this name. Please change.'
                    )
                    return render(request,
                                  'workflow/attributes.html',
                                  {'form': form})

                # Check #2: new key is not a condition name
                if new_key in condition_names:
                    form.add_error(
                        old_key,
                        'There is a condition already with this name.'
                    )
                    return render(request,
                                  'workflow/attributes.html',
                                  {'form': form})

            # Attributes are clean and good to go

            # Collect the data from the form
            new_attr = {}
            for old_key in old_keys:
                new_attr[form.cleaned_data[old_key]] = \
                    form.cleaned_data[old_key + '__value']

            try:
                # Try to translate and write in DB
                workflow.attributes = new_attr
            except TypeError:
                messages.error(request, 'Unable to store attributes. '
                                        'Edit and retry.')
                return render(request,
                              'workflow/attributes.html',
                              {'form': form})

            # Log the event
            logs.ops.put(request.user,
                         'workflow_attribute_update',
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'attr': wf_attributes})

            # Save record
            workflow.save()

            return redirect('workflow:detail', workflow.id)

    return render(request,
                  'workflow/attributes.html',
                  {'form': form})


@user_passes_test(is_instructor)
def attribute_create(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False

    # Create the form object with the form_fields just computed
    form = AttributeItemForm(request.POST or None,
                             keys=workflow.attributes.keys())

    if request.method == 'POST':
        if form.is_valid():
            # Enforce the property that Attribute names, column names and
            #  condition names cannot overlap.
            attr_name = form.cleaned_data['key']
            if attr_name in workflow.get_column_names():
                form.add_error(
                    'key',
                    'There is a column with this name. Please change.'
                )
                data['html_form'] = render_to_string(
                    'workflow/includes/partial_attribute_create.html',
                    {'form': form},
                    request=request)

                return JsonResponse(data)

            # Check if there is a condition with that name
            conditions = Condition.objects.filter(action__workflow=workflow)
            if attr_name in [x.name for x in conditions]:
                form.add_error(
                    'key',
                    'There is a condition already with this name.'
                )
                data['html_form'] = render_to_string(
                    'workflow/includes/partial_attribute_create.html',
                    {'form': form},
                    request=request)

                return JsonResponse(data)

            # proceed with updating the attributes.
            wf_attributes = workflow.attributes
            wf_attributes[form.cleaned_data['key']] = \
                form.cleaned_data['value']

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

    data['html_form'] = render_to_string(
        'workflow/includes/partial_attribute_create.html',
        {'form': form},
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def attribute_delete(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False
    key = request.GET.get('key', None)

    if request.method == 'POST' and key is not None:

        wf_attributes = workflow.attributes
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
    else:
        key = request.GET['key']

    data['html_form'] = render_to_string(
        'workflow/includes/partial_attribute_delete.html',
        {'key': key},
        request=request)

    return JsonResponse(data)
