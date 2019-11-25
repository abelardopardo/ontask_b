# -*- coding: utf-8 -*-

"""Functions to manipulate access to workflows."""

from typing import List, Optional, Union

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ontask import OnTaskException
from ontask import models


def access(
    request,
    wid: Optional[int],
    select_related: Optional[Union[str, List]] = None,
    prefetch_related:  Optional[Union[str, List]] = None,
) -> Optional[models.Workflow]:
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
        models.Workflow.unlock_workflow_by_id(sid)

    with cache.lock('ONTASK_WORKFLOW_{0}'.format(wid)):

        # Step 1: Get the workflow that is being accessed
        workflow = models.Workflow.objects.filter(id=wid).filter(
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
        user_id = session.get_decoded().get('_auth_user_id')
        if not user_id:
            # Session has no user_id, so proceed to lock the workflow
            return wf_lock_and_update(request, workflow)

        owner = get_user_model().objects.get(id=user_id)

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
    workflow: models.Workflow,
    create_session: Optional[bool] = False,
) -> models.Workflow:
    """Lock a workflow and updates the value in the session.

    :param request: Http request to update
    :param workflow: Workflow being modified
    :param create_session: Boolean encoding if a session needs to be created.
    :param workflow: Object to store
    """
    workflow.lock(request, create_session)
    # Update nrows in case it was asynch modified
    store_workflow_nrows_in_session(request, workflow)

    return workflow


def store_workflow_nrows_in_session(
    request: HttpRequest,
    wflow: models.Workflow
):
    """Store the workflow id and name in the request.session dictionary.

    :param request: Request object
    :param wflow: Workflow object
    :return: Nothing. Store the id and the name in the session
    """
    request.session['ontask_workflow_rows'] = wflow.nrows
    request.session.save()


def store_workflow_in_session(request: HttpRequest, wflow: models.Workflow):
    """Store the workflow id, name, and number of rows in the session.

    :param request: Request object
    :param wflow: Workflow object
    :return: Nothing. Store the id, name and nrows in the session
    """
    request.session['ontask_workflow_id'] = wflow.id
    request.session['ontask_workflow_name'] = wflow.name
    store_workflow_nrows_in_session(request, wflow)


def remove_workflow_from_session(request: HttpRequest):
    """Remove the workflowid, name and number of fows from the session."""
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        models.Workflow.unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)
    request.session.pop('ontask_workflow_rows', None)
    request.session.save()
