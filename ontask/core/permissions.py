# -*- coding: utf-8 -*-

"""Basic functions and classes to check for permissions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import base, detail
from rest_framework import permissions

from ontask import models
from ontask.core.session_ops import (
    SessionStore, acquire_workflow_access, expand_query_with_related)

GROUP_NAMES = ['student', 'instructor']

workflow_no_data_error_message = _(
    'Workflow has no data. Go to "Manage table data" to upload data.')


def error_redirect(
    request: http.HttpRequest,
    where: Optional[str] = 'home',
    message: Optional[str] = None,
) -> http.HttpResponse:
    """Redirect the response when an error has been detected.

    :param request: Request received (used to check if is an ajax one
    :param where: URL name to redirect (home by default)
    :param message: Message to add to the request
    :return: HttpResponse
    """
    if message:
        messages.error(request, message)
    if request.is_ajax():
        return http.JsonResponse({'html_redirect': reverse(where)})
    return redirect(where)


def store_workflow_in_session(session: SessionStore, wflow: models.Workflow):
    """Store the workflow id, name, and number of rows in the session.

    :param session: object of SessionStore
    :param wflow: Workflow object
    :return: Nothing. Store the id, name and nrows in the session
    """
    session['ontask_workflow_id'] = wflow.id
    session['ontask_workflow_name'] = wflow.name
    session['ontask_workflow_rows'] = wflow.nrows


def get_session_workflow(
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
    workflow = acquire_workflow_access(
        request.user,
        request.session,
        wid=wid,
        select_related=s_related,
        prefetch_related=pf_related)

    store_workflow_in_session(request.session, workflow)

    return workflow


def is_instructor(user) -> bool:
    """Check if the user is authenticated and belongs to the instructor group.

    @DynamicAttrs

    :param user: User object
    :return: Boolean stating if user belongs to the group
    """
    return (
        user.is_authenticated
        and (
            user.groups.filter(name='instructor').exists()
            or user.is_superuser
        )
    )


def is_admin(user) -> bool:
    """Check if the user is authenticated and is supergroup.

    @DynamicAttrs

    :param user: User object
    :return: Boolean stating if user is admin
    """
    return user.is_authenticated and user.is_superuser


def has_access(user, workflow):
    """Calculate if user has access to workflow.

    :param user: User object
    :param workflow: Workflow object
    :return: True if it is owner or in the shared list
    """
    return workflow.user == user or user in workflow.shared.all()


class IsOwner(permissions.BasePermission):
    """Custom permission to only allow owners of an object to access it."""

    def has_object_permission(self, request, view, obj):
        """Check if obj.user and request user are the same."""
        # Access only allowed to the "user" field of the object.
        return obj.user == request.user


class UserIsInstructor(UserPassesTestMixin, permissions.BasePermission):
    """Use in views to allow only instructors to access.

    @DynamicAttrs
    """

    def test_func(self):
        """Overwrite the user passes test mixing function."""
        return is_instructor(self.request.user)

    def has_permission(self, request, view):
        """Equivalent to has permission."""
        return is_instructor(request.user)

    def has_object_permission(self, request, view, obj_param):
        """Simply check if it is instructor."""
        del view, obj_param
        return is_instructor(request.user)


class UserIsAdmin(UserPassesTestMixin, permissions.BasePermission):
    """Use in views to allow access only to admin users.

    @DynamicAttrs
    """

    def test_func(self):
        """Overwrite the user passes test mixing function."""
        return is_admin(self.request.user)

    def has_permission(self, request, view):
        """Equivalent to has permission."""
        return is_admin(request.user)

    def has_object_permission(self, request, view, obj_param):
        """Simply check if it is admin."""
        del view, obj_param
        return is_admin(request.user)


class JSONResponseMixin(base.TemplateResponseMixin):
    """Renders a JSON response."""

    def render_to_response(self, context, **response_kwargs):
        """Return a JSON response."""
        return http.JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """Return the object to serialize and include in the JSON response."""
        return context


class JSONFormResponseMixin(JSONResponseMixin):
    """Renders a JSON response with html_form: <FORM HTML CODE>"""

    def get_data(self, context):
        """Return the form serialized to include in the JSON response."""
        return {'html_form': render_to_string(
            self.template_name,
            context,
            request=self.request)}


class WorkflowView(base.View):
    """View that sets the workflow attribute."""

    def __init__(self, **kwargs):
        """Initialise error field/redirect and the workflow attribute."""
        super().__init__(**kwargs)
        self.error_message = None
        self.error_redirect = 'home'
        self.workflow = None
        self.object = None

    def setup(self, request, *args, **kwargs):
        """Add workflow attribute to view object.

        The query uses the two variables:
        - wf_s_related: Workflow select related
        - wf_pf_related: Workflow prefetch related
        If there is any problem, the exception message is stored instead.
        """
        super().setup(request, *args, **kwargs)
        try:
            self.workflow = get_session_workflow(
                request,
                kwargs.get('wid'),
                getattr(self, 'wf_s_related', None),
                getattr(self, 'wf_pf_related', None))
        except Exception as exc:
            self.workflow = None
            self.error_message = _(
                'Unable to detect workflow ({0}).').format(str(exc))

    def get_object(self, queryset=None):
        """Bypass request for object returning the existing attribute."""
        return self.workflow

    def dispatch(self, request, *args, **kwargs):
        """Intercept if there has been any error."""
        if self.error_message:
            return error_redirect(
                request,
                where=self.error_redirect,
                message=_('ERROR: ') + self.error_message)
        return super().dispatch(request, *args, **kwargs)


class ActionView(detail.SingleObjectMixin, WorkflowView):
    """View that restricts action to be part of the workflow."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)

        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the actions attached to this workflow."""
        return expand_query_with_related(
            self.workflow.actions.all(),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class ColumnConditionView(detail.SingleObjectMixin, WorkflowView):
    """View that restricts Column/Condition tuple be part of the workflow."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)

        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""

        return expand_query_with_related(
            models.ActionColumnConditionTuple.objects.filter(
                Q(action__workflow__user=self.request.user)
                | Q(action__workflow__shared=self.request.user),
                action__workflow=self.workflow),
            getattr(self, 's_related', ['action', 'condition', 'column']),
            getattr(self, 'pf_related', None))


class ColumnView(detail.SingleObjectMixin, WorkflowView):
    """View that sets a column in the workflow as object."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)
        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'dataops:uploadmerge'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""

        return expand_query_with_related(
            self.workflow.columns.all(),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class ConditionView(detail.SingleObjectMixin, WorkflowView):
    """View that sets the object as a workflow condition."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)
        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""

        return expand_query_with_related(
            self.workflow.conditions.all(),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class LogView(detail.SingleObjectMixin, WorkflowView):
    """View that sets tthe object as a workflow log."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)
        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""

        return expand_query_with_related(
            self.workflow.logs.filter(user=self.request.user),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class ScheduledOperationView(detail.SingleObjectMixin, WorkflowView):
    """View that sets object as a scheduled op in the workflow."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)
        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""
        return expand_query_with_related(
            self.workflow.scheduled_operations.all(),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class ViewView(detail.SingleObjectMixin, WorkflowView):
    """View that sets the object as a view."""

    def setup(self, request, *args, **kwargs):
        """Check that the workflow has data."""
        super().setup(request, *args, **kwargs)
        if not self.workflow:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'

    def get_queryset(self):
        """Consider only the items attached to this workflow."""
        return expand_query_with_related(
            self.workflow.views.all(),
            getattr(self, 's_related', None),
            getattr(self, 'pf_related', None))


class SingleViewMixin(detail.SingleObjectMixin):
    """Select a table view in Class-based Views."""
    model = models.View

    context_object_name = 'table_view'

    def get_object(self, queryset=None) -> models.View:
        """Access the table_view in the View."""
        return self.table_view
