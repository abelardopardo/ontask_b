# -*- coding: utf-8 -*-

"""Decorators for functions in OnTask."""
from functools import wraps

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.workflow.access import access, store_workflow_in_session


def ajax_required(func):
    """Verify that the request is AJAX."""
    @wraps(func)
    def function_wrapper(request, *args, **kwargs):  # noqa Z430
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)

    return function_wrapper


def get_workflow(
    s_related: object = None,
    pf_related: object = None,
):
    """Check that the request has the correct workflow stored.

    It also passes the select_related and prefetch_related fields.

    :param wid: A workflow ID to use if there is no object stored in the
    request.

    :param s_related: select_related to use when fetching the workflow

    :param pf_related: prefetch_re  lated to use when fetching the workflow

    """
    def get_workflow_decorator(func):  # noqa Z430
        @wraps(func)  # noqa Z430
        def function_wrapper(request, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None
            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            return func(request, **kwargs)

        return function_wrapper

    return get_workflow_decorator


def get_column(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to an action in the Workflow."""
    def get_column_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None
            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                if request.is_ajax():
                    return JsonResponse(
                        {'html_redirect': reverse('action:index')})
                return redirect(reverse('action:index'))

            if not kwargs.get('column'):
                column = workflow.columns.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not column:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['column'] = column

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_column_decorator


def get_action(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to an action in the Workflow."""
    def get_action_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None
            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                if request.is_ajax():
                    return JsonResponse(
                        {'html_redirect': reverse('action:index')})
                return redirect(reverse('action:index'))

            if not kwargs.get('action'):
                action = workflow.actions.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not action:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['action'] = action

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_action_decorator


def get_condition(
    s_related=None,
    pf_related=None,
    is_filter=False,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_condition_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None
            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                if request.is_ajax():
                    return JsonResponse(
                        {'html_redirect': reverse('action:index')})
                return redirect(reverse('action:index'))

            if not kwargs.get('condition'):
                # Get the condition
                condition = models.Condition.objects.filter(pk=pk).filter(
                    Q(action__workflow__user=request.user)
                    | Q(action__workflow__shared=request.user),
                    action__workflow=workflow,
                )
                if is_filter is not None:
                    condition = condition.filter(is_filter=is_filter)
                    # Get the condition
                condition = condition.select_related('action').first()
                if not condition:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['condition'] = condition

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_condition_decorator


def get_columncondition(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_columncondition_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None
            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                if request.is_ajax():
                    return JsonResponse(
                        {'html_redirect': reverse('action:index')})
                return redirect(reverse('action:index'))

            # Get the column-condition
            cc_tuple = models.ActionColumnConditionTuple.objects.filter(
                pk=pk).filter(
                Q(action__workflow__user=request.user)
                | Q(action__workflow__shared=request.user),
                action__workflow=workflow,
            ).select_related('action', 'condition', 'column').first()

            if not cc_tuple:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            kwargs['cc_tuple'] = cc_tuple

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_columncondition_decorator


def get_view(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_view_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            try:
                workflow = access(
                    request,
                    wid=kwargs.get('wid'),
                    select_related=s_related,
                    prefetch_related=pf_related,
                )
            except Exception as exc:
                messages.error(request, str(exc))
                workflow = None

            if not workflow:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            # Update the session
            store_workflow_in_session(request, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                if request.is_ajax():
                    return JsonResponse(
                        {'html_redirect': reverse('action:index')})
                return redirect(reverse('action:index'))

            if not kwargs.get('view'):
                # Get the view
                view = models.View.objects.filter(pk=pk).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).prefetch_related('columns').first()

                if not view:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['view'] = view

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_view_decorator
