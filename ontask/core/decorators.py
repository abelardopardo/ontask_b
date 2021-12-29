# -*- coding: utf-8 -*-

"""Decorators for functions in OnTask."""
from functools import wraps
from typing import Callable

from django import http
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core.permissions import (
    error_redirect, store_workflow_in_session, get_session_workflow)


def ajax_required(func: Callable) -> Callable:
    """Verify that the request is AJAX."""
    @wraps(func)
    def function_wrapper(request, *args, **kwargs):  # noqa Z430
        """Verify that request is ajax and if so, call func."""
        if not request.is_ajax():
            return http.HttpResponseBadRequest()
        return func(request, *args, **kwargs)

    return function_wrapper


def get_workflow(
    s_related: object = None,
    pf_related: object = None,
) -> Callable:
    """Check that the request has the correct workflow stored.

    It also passes the select_related and prefetch_related fields.

    :param s_related: select_related to use when fetching the workflow
    :param pf_related: prefetch_related to use when fetching the workflow
    """
    def get_workflow_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa Z430
        def function_wrapper(request, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            return func(request, **kwargs)

        return function_wrapper

    return get_workflow_decorator


def get_column(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to an action in the Workflow."""
    def get_column_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            if not kwargs.get('column'):
                column = workflow.columns.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not column:
                    return error_redirect(request)

                kwargs['column'] = column

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_column_decorator


def get_action(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to an action in the Workflow."""
    def get_action_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            if not kwargs.get('action'):
                action = workflow.actions.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not action:
                    return error_redirect(request)

                kwargs['action'] = action

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_action_decorator


def get_condition(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_condition_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            if not kwargs.get('condition'):
                # Get the condition
                condition = models.Condition.objects.filter(pk=pk).filter(
                    Q(action__workflow__user=request.user)
                    | Q(action__workflow__shared=request.user),
                    action__workflow=workflow,
                ).select_related('action').first()
                if not condition:
                    return error_redirect(request)

                kwargs['condition'] = condition

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_condition_decorator


def get_filter(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to a filter in the action."""
    def get_filter_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            if not kwargs.get('filter'):
                # Get the condition
                filter_obj = models.Filter.objects.filter(pk=pk).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                    workflow=workflow,
                ).first()
                if not filter_obj:
                    return error_redirect(request)

                kwargs['filter'] = filter_obj

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_filter_decorator


def get_columncondition(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_columncondition_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            # Get the column-condition
            cc_tuple = models.ActionColumnConditionTuple.objects.filter(
                pk=pk).filter(
                Q(action__workflow__user=request.user)
                | Q(action__workflow__shared=request.user),
                action__workflow=workflow,
            ).select_related('action', 'condition', 'column').first()

            if not cc_tuple:
                return error_redirect(request)

            kwargs['cc_tuple'] = cc_tuple

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_columncondition_decorator


def get_view(
    s_related=None,
    pf_related=None,
) -> Callable:
    """Check that the pk parameter refers to a condition in the Workflow."""
    def get_view_decorator(func):  # noqa Z430
        """Wrapper to get access to the function."""
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            """Wrapper to get access to the request."""
            try:
                workflow = get_session_workflow(
                    request,
                    kwargs.get('wid'),
                    s_related,
                    pf_related)
            except Exception:
                return error_redirect(request)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return error_redirect(request, 'action:index')

            if not kwargs.get('view'):
                # Get the view
                view = models.View.objects.filter(pk=pk).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).prefetch_related('columns').first()

                if not view:
                    return error_redirect(request)

                kwargs['view'] = view

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_view_decorator
