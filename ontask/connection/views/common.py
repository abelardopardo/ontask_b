# -*- coding: utf-8 -*-

"""Common functions to handle connections."""

from django import http
from django.utils.decorators import method_decorator
from django.views import generic

from ontask.connection import services
from ontask.core import ajax_required
from ontask.core import (
    JSONFormResponseMixin, UserIsAdmin, UserIsInstructor)


class ConnectionAdminIndexView(UserIsAdmin, generic.TemplateView):
    """Base class to view the list of connections."""

    title = None


class ConnectionIndexView(UserIsInstructor, generic.TemplateView):
    """Base class to show the connections to instructors."""

    title = None
    is_sql = False


@method_decorator(ajax_required, name='dispatch')
class ConnectionShowView(
    UserIsInstructor,
    JSONFormResponseMixin,
    generic.DetailView,
):
    """Basic view to show a connection in a modal."""

    model = None
    template = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['c_vals'] = self.object.get_display_dict()
        return context


@method_decorator(ajax_required, name='dispatch')
class ConnectionBaseCreateEditView(UserIsAdmin, JSONFormResponseMixin):
    """Base class to Create/Edit a new view."""

    template_name = 'connection/includes/partial_addedit.html'
    action_url = None
    event_type = None

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})
        conn = form.save()
        conn.log(self.request.user, self.event_type)
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConnectionDeleteView(
    UserIsAdmin,
    JSONFormResponseMixin,
    generic.DeleteView,
):
    """Delete an SQL connection."""

    model = None
    template_name = 'connection/includes/partial_delete.html'
    object = None

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.log(request.user, self.object.delete_event)
        self.object.delete()
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConnectionCloneView(
    UserIsAdmin,
    JSONFormResponseMixin,
    generic.DetailView,
):
    """Process the Clone Connection view."""

    model = None
    http_method_names = ['get', 'post']
    template_name = 'connection/includes/partial_clone.html'

    def post(self, request, *args, **kwargs):
        services.clone_connection(
            request,
            self.get_object(),
            self.model.objects)
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConnectionToggleView(
    UserIsAdmin,
    JSONFormResponseMixin,
    generic.DetailView,
):
    """Process the Toggle Connection view."""

    model = None
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        conn = self.get_object()
        conn.enabled = not conn.enabled
        conn.save(update_fields=['enabled'])
        conn.log(request.user, conn.toggle_event, enabled=conn.enabled)
        return http.JsonResponse({'is_checked': conn.enabled})


