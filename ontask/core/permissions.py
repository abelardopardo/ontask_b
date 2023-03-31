# -*- coding: utf-8 -*-

"""Basic functions and classes to check for permissions."""
from typing import List, Optional, Union

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
from ontask.core.session_ops import SessionStore, acquire_workflow_access

GROUP_NAMES = ['student', 'instructor']


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


class JSONResponseMixin(base.TemplateResponseMixin):
    """Renders a JSON response."""

    def render_to_response(self, context, **response_kwargs):
        """Return a JSON response."""
        return http.JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """Return the object to serialize and include in the JSON response."""
        return None


class JSONFormResponseMixin(JSONResponseMixin):
    """Renders a JSON response with html_form: <FORM HTML CODE>"""

    def get_data(self, context):
        """Return the form serialized to incluce in the JSON response."""
        return {'html_form': render_to_string(
            self.template_name,
            context,
            request=self.request)}


class RequestWorkflowView(base.View):
    """Store session workflow in View."""
    workflow = None
    s_related: Optional[Union[str, List]] = None
    pf_related: Optional[Union[str, List]] = None

    def dispatch(self, request, *args, **kwargs):
        """Get the workflow, store it in object, and dispatch."""
        try:
            self.workflow = get_session_workflow(
                request,
                kwargs.get('wid'),
                self.s_related,
                self.pf_related)
        except Exception as exc:
            return error_redirect(request, message=str(exc))

        return super().dispatch(request, *args, **kwargs)


class SingleWorkflowMixin(detail.SingleObjectMixin):
    """Class to handle workflow in class-based views"""
    model = models.Workflow
    pk_url_kwarg = 'wid'
    s_related: Optional[Union[str, List]] = None
    pf_related: Optional[Union[str, List]] = None

    def get_object(self, queryset=None):
        """Return workflow, and store it in the session."""

        return get_session_workflow(
            self.request,
            self.kwargs.get(self.pk_url_kwarg),
            self.s_related,
            self.pf_related)


class SingleActionMixin(detail.SingleObjectMixin, RequestWorkflowView):
    """Store action in View."""

    model = models.Action

    def get_object(self, queryset=None) -> models.Action:
        """Access the Action verify that belongs to workflow."""
        act_obj = super().get_object(queryset=queryset)
        if act_obj.workflow != self.workflow:
            raise http.Http404(_('Action does not belong to current workflow'))

        return act_obj


class RequestColumnView(RequestWorkflowView):
    """Store column in View."""
    column = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(_(
                'Workflow has no data. '
                'Go to "Manage table data" to upload data.'))

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


class RequestConditionView(RequestWorkflowView):
    """Store Condition in View."""
    condition = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(_(
                'Workflow has no data. '
                'Go to "Manage table data" to upload data.'))

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


class RequestFilterView(RequestWorkflowView):
    """Store Filter in View."""
    filter = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(_(
                'Workflow has no data. '
                'Go to "Manage table data" to upload data.'))

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


class RequestColumnConditionView(RequestWorkflowView):
    """Store ColumnCondition in View."""
    column_condition = None

    def set_object(self, request, *args, **kwargs):
        """Set the workflow object."""
        super().set_object(request, *args, **kwargs)

        if self.workflow.nrows == 0:
            raise http.Http404(_(
                'Workflow has no data. '
                'Go to "Manage table data" to upload data.'))

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


def is_admin(user):
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
