# -*- coding: utf-8 -*-

"""Functions to implement CRUD views for Views."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import OnTaskServiceException, create_new_name, models
from ontask.core import ajax_required, get_view, get_workflow, is_instructor
from ontask.table import forms, services


@user_passes_test(is_instructor)
@get_workflow(pf_related='views')
def view_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the list of views attached to a workflow.

    :param request: Http request received.
    :param workflow: Workflow being processed
    :return: HTTP response with the table
    """
    # Get the views
    views = workflow.views.values(
        'id',
        'name',
        'description_text',
        'modified')

    # Build the table only if there is anything to show (prevent empty table)
    return render(
        request,
        'table/view_index.html',
        {
            'query_builder_ops': workflow.get_query_builder_ops_as_str(),
            'table': services.ViewTable(views, orderable=False),
        },
    )


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='columns')
def view_add(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Create a new view.

    :param request: Request object
    :param workflow: Workflow being processed
    :return: AJAX response
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add a view to a workflow without data'))
        return http.JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = forms.ViewAddForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = form.save(commit=False)
        services.save_view_form(request.user, workflow, view)
        form.save_m2m()  # Needed to propagate the save effect to M2M relations

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_add.html',
            {'form': form, 'id': form.instance.id},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_edit(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Edit the content of a view.

    :param request: Request object
    :param workflow: Workflow being processed
    :param pk: Primary key of the view
    :param view: View to be edited
    :return: AJAX Response
    """
    del pk
    form = forms.ViewAddForm(
        request.POST or None,
        instance=view, workflow=workflow)
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = form.save(commit=False)
        services.save_view_form(request.user, workflow, view)
        form.save_m2m()  # Needed to propagate the save effect to M2M relations

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_edit.html',
            {'form': form, 'id': form.instance.id},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_delete(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Delete a view.

    AJAX processor for the delete view operation

    :param request: AJAX request
    :param workflow: Workflow being processed
    :param pk: primary key of the view to delete
    :param view: View to be deleted.
    :return: AJAX response to handle the form.
    """
    del pk, workflow
    if request.method == 'POST':
        view.log(request.user, models.Log.VIEW_DELETE)
        view.delete()
        return http.JsonResponse({'html_redirect': reverse('table:view_index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_delete.html',
            {'view': view},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_clone(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> http.JsonResponse:
    """Clone a view.

    :param request: HTTP request
    :param pk: ID of the view to clone. The workflow is taken from the session
    :param workflow: Workflow being processed
    :param view: View to be cloned.
    :return: AJAX response
    """
    if request.method == 'GET':
        return http.JsonResponse({
            'html_form': render_to_string(
                'table/includes/partial_view_clone.html',
                {'pk': pk, 'vname': view.name},
                request=request)})

    try:
        services.do_clone_view(
            request.user,
            view,
            new_workflow=None,
            new_name=create_new_name(view.name, workflow.views)
        )
    except OnTaskServiceException as exc:
        exc.message_to_error(request)
        exc.delete()
    return http.JsonResponse({'html_redirect': ''})
