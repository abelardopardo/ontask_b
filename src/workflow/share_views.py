# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

from logs.models import Log
from ontask.decorators import get_workflow
from ontask.permissions import is_instructor
from .forms import SharedForm


@user_passes_test(is_instructor)
def share_create(request):
    """Add a new user to the list of those sharing the workflow.

    :param request:

    :return:
    """
    # Get the workflow
    workflow = get_workflow(request, prefetch_related='shared')
    if not workflow:
        return redirect('home')

    # Create the form object with the form_fields just computed
    form = SharedForm(
        request.POST or None,
        user=request.user,
        workflow=workflow)

    if request.method == 'POST':
        if form.is_valid():
            # proceed with the update
            workflow.shared.add(form.user_obj)
            workflow.save()

            # Log the event
            Log.objects.register(
                request.user,
                Log.WORKFLOW_SHARE_ADD,
                workflow,
                {
                    'id': workflow.id,
                    'name': workflow.name,
                    'user_email': form.user_obj.email})

            return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_share_create.html',
            {'form': form},
            request=request)
    })


@user_passes_test(is_instructor)
def share_delete(request, pk):
    """Delete one of the users sharing the workflow.

    :param request:

    :param pk:

    :return:
    """
    # Get the workflow
    workflow = get_workflow(request, prefetch_related='shared')
    if not workflow:
        return redirect('home')

    # If the user does not exist, go back to home page
    user = get_user_model().objects.filter(id=pk).first()
    if not user:
        return redirect('home')

    if request.method == 'POST':
        workflow.shared.remove(user)
        workflow.save()

        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_SHARE_DELETE,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name,
                'user_email': user.email})

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_share_delete.html',
            {'uid': pk, 'uemail': user.email},
            request=request)
    })
