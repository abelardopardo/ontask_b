# -*- coding: utf-8 -*-

"""Decorators for functions in OnTask."""
from functools import wraps
from typing import Callable, Optional

from django import http
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.core.session_ops import SessionStore, acquire_workflow_access


def _get_requested_workflow(
    request: http.HttpRequest,
    wid: int = None,
    s_related: object = None,
    pf_related: object = None,
) -> Optional[models.Workflow]:
    """Access the requested workflow.

    :param request: HTTP request received
    :param s_related: select_related to use when fetching the workflow
    :param pf_related: prefetch_related to use when fetching the workflow
    :param wid: ID of the requested workflow
    :return
    """
    try:
        workflow = acquire_workflow_access(
            request.user,
            request.session,
            wid=wid,
            select_related=s_related,
            prefetch_related=pf_related)
    except Exception as exc:
        messages.error(request, str(exc))
        workflow = None

    return workflow


def _error_redirect(
    request: http.HttpRequest,
    where: Optional[str] = 'home'
) -> http.HttpResponse:
    """Redirect the response when an error has been detected.

    :param request: Request received (used to check if is an ajax one
    :param where: URL name to redirect (home by default)
    :return: HttpResponse
    """
    if request.is_ajax():
        return http.JsonResponse({'html_redirect': reverse(where)})
    return redirect(where)


def ajax_required(func: Callable) -> Callable:
    """Verify that the request is AJAX."""
    @wraps(func)
    def function_wrapper(request, *args, **kwargs):  # noqa Z430
        """Verify that request is ajax and if so, call func."""
        if not request.is_ajax():
            return http.HttpResponseBadRequest()
        return func(request, *args, **kwargs)

    return function_wrapper


def store_workflow_in_session(session: SessionStore, wflow: models.Workflow):
    """Store the workflow id, name, and number of rows in the session.

    :param session: object of SessionStore
    :param wflow: Workflow object
    :return: Nothing. Store the id, name and nrows in the session
    """
    session['ontask_workflow_id'] = wflow.id
    session['ontask_workflow_name'] = wflow.name
    session['ontask_workflow_rows'] = wflow.nrows


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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)

            if not workflow:
                return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            if not kwargs.get('column'):
                column = workflow.columns.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not column:
                    return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            if not kwargs.get('action'):
                action = workflow.actions.filter(
                    pk=pk,
                ).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).first()
                if not action:
                    return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            if not kwargs.get('condition'):
                # Get the condition
                condition = models.Condition.objects.filter(pk=pk).filter(
                    Q(action__workflow__user=request.user)
                    | Q(action__workflow__shared=request.user),
                    action__workflow=workflow,
                ).select_related('action').first()
                if not condition:
                    return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            if not kwargs.get('filter'):
                # Get the condition
                filter_obj = models.Filter.objects.filter(pk=pk).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                    workflow=workflow,
                ).select_related('action').first()
                if not filter_obj:
                    return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            # Get the column-condition
            cc_tuple = models.ActionColumnConditionTuple.objects.filter(
                pk=pk).filter(
                Q(action__workflow__user=request.user)
                | Q(action__workflow__shared=request.user),
                action__workflow=workflow,
            ).select_related('action', 'condition', 'column').first()

            if not cc_tuple:
                return _error_redirect(request)

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
            workflow = _get_requested_workflow(
                request,
                kwargs.get('wid'),
                s_related,
                pf_related)
            if not workflow:
                return _error_redirect(request)

            # Update the session
            store_workflow_in_session(request.session, workflow)

            kwargs['workflow'] = workflow

            if workflow.nrows == 0:
                messages.error(
                    request,
                    _('Workflow has no data. '
                      + 'Go to "Manage table data" to upload data.'),
                )
                return _error_redirect(request, 'action:index')

            if not kwargs.get('view'):
                # Get the view
                view = models.View.objects.filter(pk=pk).filter(
                    Q(workflow__user=request.user)
                    | Q(workflow__shared=request.user),
                ).prefetch_related('columns').first()

                if not view:
                    return _error_redirect(request)

                kwargs['view'] = view

            return func(request, pk, **kwargs)

        return function_wrapper

    return get_view_decorator
