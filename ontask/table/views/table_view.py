# -*- coding: utf-8 -*-

"""Functions to implement CRUD views for Views."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask import OnTaskServiceException, create_new_name, models
from ontask.condition.forms import FilterForm
from ontask.core import ajax_required, get_view, get_workflow, is_instructor
from ontask.table import forms, services


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

    # Forms to read/process data
    view_form = forms.ViewAddForm(request.POST or None, workflow=workflow)
    filter_form = FilterForm(request.POST or None, include_description=False)

    if (
        request.method == 'POST' and
        view_form.is_valid() and
        filter_form.is_valid()
    ):
        if not view_form.has_changed() and not filter_form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = view_form.save(commit=False)
        filter_obj = filter_form.save(commit=False)

        services.save_view_form(request.user, workflow, view, filter_obj)
        # Propagate the save effect to M2M relations
        view_form.save_m2m()

        return http.JsonResponse({
            'html_redirect': reverse(
                'table:display_view',
                kwargs={'pk': view.id})})

    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_add.html',
            {
                'id': view_form.instance.id,
                'view_form': view_form,
                'filter_form': filter_form},
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

    # Forms to read/process data
    v_form = forms.ViewAddForm(
        request.POST or None,
        instance=view, workflow=workflow)
    f_form = FilterForm(
        request.POST or None,
        instance=view.filter,
        include_description=False)

    if (
        request.method == 'POST' and
        v_form.is_valid() and
        f_form.is_valid()
    ):
        if not v_form.has_changed() and not f_form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = v_form.save(commit=False)
        filter_obj = f_form.save(commit=False)

        services.save_view_form(request.user, workflow, view, filter_obj)
        # Propagate the save effect to M2M relations
        v_form.save_m2m()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_edit.html',
            {'id': v_form.instance.id, 'v_form': v_form, 'f_form': f_form},
            request=request)})


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
        if view.filter:
            view.filter.delete_from_view()
        view.delete()
        return http.JsonResponse({'html_redirect': reverse('table:display')})

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
