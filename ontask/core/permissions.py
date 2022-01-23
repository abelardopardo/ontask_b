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
    """View that sets the action attribute."""

    model = models.Action

    def setup(self, request, *args, **kwargs):
        """Add action attribute to view object."""
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
    """View that sets the cc_tuple attribute."""

    def setup(self, request, *args, **kwargs):
        """Add column condition attribute to view object."""
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


class ColumnView(WorkflowView):
    """View that sets the column attribute."""

    def __init__(self, **kwargs):
        """Initialise the column attribute."""
        super().__init__(**kwargs)
        self.column = None

    def setup(self, request, *args, **kwargs):
        """Add column attribute to view object."""
        super().setup(request, *args, **kwargs)
        if not self.workflow:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'
            return

        self.column = self.workflow.columns.filter(pk=kwargs.get('pk')).first()
        if not self.column:
            self.error_message = _('Incorrect column/condition tuple.')
            return


class ConditionView(WorkflowView):
    """View that sets the condition attribute."""

    def __init__(self, **kwargs):
        """Initialise the condition attribute."""
        super().__init__(**kwargs)
        self.condition = None

    def setup(self, request, *args, **kwargs):
        """Add column attribute to view object."""
        super().setup(request, *args, **kwargs)
        if not self.workflow:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'
            return

        self.condition = self.workflow.conditions.filter(
            pk=kwargs.get('pk')).first()

        if not self.condition:
            return error_redirect(request)


class ScheduledOperationView(WorkflowView):
    """View that sets the scheduled operation attribute."""

    def __init__(self, **kwargs):
        """Initialise the scheduled operation attribute."""
        super().__init__(**kwargs)
        self.scheduled_operation = None

    def setup(self, request, *args, **kwargs):
        """Add scheduled operation attribute to view object."""
        super().setup(request, *args, **kwargs)
        if not self.workflow:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'
            return

        self.scheduled_operation = self.workflow.scheduled_operations.filter(
            pk=kwargs.get('pk')).first()

        if not self.scheduled_operation:
            return error_redirect(request)


class ViewView(WorkflowView):
    """View that sets the table_view operation attribute."""

    def __init__(self, **kwargs):
        """Initialise the view operation attribute."""
        super().__init__(**kwargs)
        self.table_view = None

    def setup(self, request, *args, **kwargs):
        """Add view attribute to view object."""
        super().setup(request, *args, **kwargs)
        if not self.workflow:
            return

        if self.workflow.nrows == 0:
            self.error_message = workflow_no_data_error_message
            self.error_redirect = 'action:index'
            return

        self.table_view = self.workflow.views.filter(
            pk=kwargs.get('pk')).first()

        if not self.table_view:
            return error_redirect(request)


class SingleColumnMixin(detail.SingleObjectMixin):
    """Select a Column in Class-based Views."""
    model = models.Column

    def get_object(self, queryset=None) -> models.Column:
        """Access the column in the View."""
        return self.column


class SingleColumnConditionMixin(detail.SingleObjectMixin):
    """Select a Column in Class-based Views."""
    model = models.ActionColumnConditionTuple

    def get_object(self, queryset=None) -> models.ActionColumnConditionTuple:
        """Access the column/condition tuple in the View."""
        return self.cc_tuple


class SingleConditionMixin(detail.SingleObjectMixin):
    """Select a Condition in Class-based Views."""
    model = models.Condition

    def get_object(self, queryset=None) -> models.Condition:
        """Access the condition tuple in the View."""
        return self.condition


class SingleViewMixin(detail.SingleObjectMixin):
    """Select a table view in Class-based Views."""
    model = models.View

    context_object_name = 'table_view'

    def get_object(self, queryset=None) -> models.View:
        """Access the table_view in the View."""
        return self.table_view


class RequestColumnView(WorkflowView):
    """Store column in View."""
    column = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(workflow_no_data_error_message)

        column = self.workflow.columns.filter(
            pk=self.kwargs.get(self.pk_url_kwarg)).filter(
            Q(workflow__user=request.user)
            | Q(workflow__shared=request.user),
        ).first()
        if not column:
            raise http.Http404(_('No column found matching the query'))

        self.column = column

    def dispatch(self, request, *args, **kwargs):
        """Get the column, store it in object, and dispatch."""
        try:
            self.set_object(request, *args, **kwargs)
        except Exception as exc:
            return error_redirect(request, 'action:index', str(exc))

        return super().dispatch(request, *args, **kwargs)


class RequestConditionView(WorkflowView):
    """Store Condition in View."""
    condition = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(workflow_no_data_error_message)

        condition = models.Condition.objects.filter(
            pk=self.kwargs.get(self.pk_url_kwarg)).filter(
            Q(workflow__user=request.user)
            | Q(workflow__shared=request.user),
            action__workflow=self.workflow).select_related('action').first()
        if not condition:
            raise http.Http404(_('No condition found matching the query'))

        self.condition = condition

    def dispatch(self, request, *args, **kwargs):
        """Get the condition, store it in object, and dispatch."""
        try:
            self.set_object(request, *args, **kwargs)
        except Exception as exc:
            return error_redirect(request, 'action:index', str(exc))

        return super().dispatch(request, *args, **kwargs)


class RequestFilterView(WorkflowView):
    """Store Filter in View."""
    filter = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(workflow_no_data_error_message)

        filter_obj = models.Filter.objects.filter(
            pk=self.kwargs.get(self.pk_url_kwarg)).filter(
            Q(workflow__user=request.user)
            | Q(workflow__shared=request.user),
            workflow=self.workflow).select_related('action').first()
        if not filter_obj:
            raise http.Http404(_('No filter found matching the query'))

        self.filter = filter_obj

    def dispatch(self, request, *args, **kwargs):
        """Get the filter, store it in object, and dispatch."""
        try:
            self.set_object(request, *args, **kwargs)
        except Exception as exc:
            return error_redirect(request, 'action:index', str(exc))

        return super().dispatch(request, *args, **kwargs)


class RequestColumnConditionView(WorkflowView):
    """Store ColumnCondition in View."""
    column_condition = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(workflow_no_data_error_message)

        cc_tuple = models.ActionColumnConditionTuple.objects.filter(
            pk=self.kwargs.get(self.pk_url_kwarg)).filter(
            Q(workflow__user=request.user)
            | Q(workflow__shared=request.user),
            action__workflow=self.workflow).select_related(
            'action', 'condition', 'column').first()
        if not cc_tuple:
            raise http.Http404(
                _('No column/condition found matching the query'))

        self.column_condition = cc_tuple

    def dispatch(self, request, *args, **kwargs):
        """Get the column/condition, store it in object, and dispatch."""
        try:
            self.set_object(request, *args, **kwargs)
        except Exception as exc:
            return error_redirect(request, 'action:index', str(exc))

        return super().dispatch(request, *args, **kwargs)


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
