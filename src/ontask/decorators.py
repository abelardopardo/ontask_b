# -*- coding: utf-8 -*-

"""Decorators for functions in OnTask."""

from functools import wraps
from typing import List, Optional, Union

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from action.models import Condition, ActionColumnConditionTuple
from ontask import OnTaskException
from table.models import View
from workflow.models import Workflow
from workflow.ops import (
    store_workflow_in_session, store_workflow_nrows_in_session,
)


def get_workflow(
    s_related: object = None,
    pf_related: object = None,
):
    """Check that the request has the correct workflow stored.

    It also passes the select_related and prefetch_related fields.

    :param wid: A workflow ID to use if there is no object stored in the
    request.

    :param s_related: select_related to use when fetching the workflow

    :param pf_related: prefetch_related to use when fetching the workflow

    """
    def get_workflow_decorator(func):  # noqa Z430
        @wraps(func)  # noqa Z430
        def function_wrapper(request, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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
    def check_column_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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

    return check_column_decorator


def get_action(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to an action in the Workflow."""
    def check_action_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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

    return check_action_decorator


def get_condition(
    s_related=None,
    pf_related=None,
    is_filter=False,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def check_condition_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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
                condition = Condition.objects.filter(pk=pk).filter(
                    Q(action__workflow__user=request.user) |
                    Q(action__workflow__shared=request.user),
                    is_filter=is_filter,
                    action__workflow=workflow,
                ).select_related('action').first()

                if not condition:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['condition'] = condition

            return func(request, pk, **kwargs)

        return function_wrapper

    return check_condition_decorator


def get_columncondition(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def check_columncondition_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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
            cc_tuple = ActionColumnConditionTuple.objects.filter(
                pk=pk).filter(
                Q(action__workflow__user=request.user)
                | Q(action__workflow__shared=request.user),
                action__workflow=workflow,
            ).select_related(['action', 'condition', 'column']).first()

            if not cc_tuple:
                if request.is_ajax():
                    return JsonResponse({'html_redirect': reverse('home')})
                return redirect('home')

            kwargs['cc_tuple'] = cc_tuple

            return func(request, pk, **kwargs)

        return function_wrapper

    return check_columncondition_decorator


def get_view(
    s_related=None,
    pf_related=None,
):
    """Check that the pk parameter refers to a condition in the Workflow."""
    def check_view_decorator(func):  # noqa Z430
        @wraps(func)  # noqa: Z430
        def function_wrapper(request, pk, **kwargs):  # noqa Z430
            workflow = access_workflow(
                request,
                wid=kwargs.get('wid'),
                select_related=s_related,
                prefetch_related=pf_related,
            )
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
                # Get the condition
                view = View.objects.filter(pk=pk).filter(
                    Q(action__workflow__user=request.user)
                    | Q(action__workflow__shared=request.user),
                ).prefetch_related('columns').first()

                if not view:
                    if request.is_ajax():
                        return JsonResponse({'html_redirect': reverse('home')})
                    return redirect('home')

                kwargs['view'] = view

            return func(request, pk, **kwargs)

        return function_wrapper

    return check_view_decorator


def access_workflow(
    request,
    wid: int,
    select_related: Optional[Union[str, List]] = None,
    prefetch_related: Optional[Union[str, List]] = None,
) -> Optional[Workflow]:
    """Verify that the workflow stored in the request can be accessed.

    :param request: HTTP request object

    :param wid: ID of the workflow that is being requested

    :param select_related: Field to add as select_related query filter

    :param prefetch_related: Field to add as prefetch_related query filter

    :return: Workflow object or raise exception with message
    """
    # Lock the workflow object while deciding if it is accessible or not to
    # avoid race conditions.
    sid = request.session.get('ontask_workflow_id')
    if wid is None and sid is None:
        # No key was given and none was found in the session (anomaly)
        return None

    if wid is None:
        # No WID provided, but the session contains one, carry on
        # with this one
        wid = sid
    elif sid != wid:
        Workflow.unlock_workflow_by_id(sid)

    with cache.lock('ONTASK_WORKFLOW_{0}'.format(wid)):

        # Step 1: Get the workflow that is being accessed
        workflow = Workflow.objects.filter(id=wid).filter(
            Q(user=request.user) | Q(shared__id=request.user.id),
        )

        if not workflow:
            return None

        # Apply select and prefetch if given
        if select_related:
            if isinstance(select_related, list):
                workflow = workflow.select_related(*select_related)
            else:
                workflow = workflow.select_related(select_related)
        if prefetch_related:
            if isinstance(prefetch_related, list):
                workflow = workflow.prefetch_related(*prefetch_related)
            else:
                workflow = workflow.prefetch_related(prefetch_related)

        # Now get the unique element from the query set
        workflow = workflow.first()

        # Step 2: If the workflow is locked by this user session, return
        # correct result (the session_key may be None if using the API)
        if request.session.session_key == workflow.session_key:
            # Update nrows. Asynch execution of plugin may have modified it
            store_workflow_nrows_in_session(request, workflow)
            return workflow

        # Step 3: If the workflow is unlocked, LOCK and return
        if not workflow.session_key:
            # Workflow is unlocked. Proceed to lock
            return wf_lock_and_update(request, workflow, create_session=True)

        # Step 4: The workflow is locked by a session different from this one.
        # See if the session locking it is still valid
        session = Session.objects.filter(
            session_key=workflow.session_key,
        ).first()
        if not session:
            # The session stored as locking the
            # workflow is no longer in the session table, so the user can
            # access the workflow
            return wf_lock_and_update(request, workflow, create_session=True)

        # Get the owner of the session locking the workflow
        owner = get_user_model().objects.get(
            id=session.get_decoded().get('_auth_user_id'))

        # Step 5: The workflow is locked by a session that is valid. See
        # if the session locking happens to be from the same user (a
        # previous session that has not been properly closed, or an API
        # call from the same user)
        if owner == request.user:
            return wf_lock_and_update(request, workflow)

        # Step 6: The workflow is locked by an existing session. See if the
        # session is valid
        if session.expire_date >= timezone.now():
            raise OnTaskException(
                _('The workflow is being modified by user {0}').format(
                    owner.email),
            )

        # The workflow is locked by a session that has expired. Take the
        # workflow and lock it with the current session.
        return wf_lock_and_update(request, workflow)


def wf_lock_and_update(
    request: HttpRequest,
    workflow: Workflow,
    create_session: Optional[bool] = False,
) -> Workflow:
    """Lock a workflow and updates the value in the session.

    :param request: Http request to update

    :param workflow: Object to store
    """
    workflow.lock(request, create_session)
    # Update nrows in case it was asynch modified
    store_workflow_nrows_in_session(request, workflow)

    return workflow


