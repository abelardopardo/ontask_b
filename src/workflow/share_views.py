# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

import logs.ops
from ontask.permissions import is_instructor
from workflow.views import WorkflowShareTable
from .forms import SharedForm
from .ops import get_workflow


@user_passes_test(is_instructor)
def share(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.user != request.user:
        # Not allowed
        messages.error(
            request,
            'You can only share workflows that you created.')
        return redirect('workflow:detail', workflow.id)

    # Show the table
    table = WorkflowShareTable(workflow.shared.values('email', 'id'))
    context = {'table': table,
               'workflow': workflow}
    return render(request, 'workflow/share.html', context)


@user_passes_test(is_instructor)
def share_create(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False

    # Create the form object with the form_fields just computed
    form = SharedForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # proceed with the update
            workflow.shared.add(form.user_obj)
            workflow.save()

            # Log the event
            logs.ops.put(request.user,
                         'workflow_share_add',
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'user_email': form.user_obj.email})

            data['form_is_valid'] = True
            data['html_redirect'] = reverse('workflow:share')
            return JsonResponse(data)

    data['html_form'] = render_to_string(
        'workflow/includes/partial_share_create.html',
        {'form': form},
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def share_delete(request):
    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False
    uemail = request.GET.get('uemail', None)

    if request.method == 'POST' and uemail is not None:
        user = get_user_model().objects.get(email=uemail)
        workflow.shared.remove(user)
        workflow.save()

        # Log the event
        logs.ops.put(request.user,
                     'workflow_share_delete',
                     workflow,
                     {'id': workflow.id,
                      'name': workflow.name,
                      'user_email': user.email})

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:share')

    data['html_form'] = render_to_string(
        'workflow/includes/partial_share_delete.html',
        {'uemail': uemail},
        request=request)

    return JsonResponse(data)
