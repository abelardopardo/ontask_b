"""Views to administer plugins."""
from typing import Dict

from django import http
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.core import (
    JSONFormResponseMixin, UserIsAdmin, UserIsInstructor,
    WorkflowView, ajax_required)
from ontask.core.session_ops import remove_workflow_from_session
from ontask.dataops import services


class PluginAdminView(UserIsInstructor, generic.TemplateView):
    """Show the table of plugins and their status."""

    template_name = 'dataops/plugin_admin.html'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)

        remove_workflow_from_session(self.request)

        # Traverse the plugin folder and refresh the db content.
        services.refresh_plugin_data(self.request)

        context['table'] = services.PluginAdminTable(
            models.Plugin.objects.all())

        return context


@method_decorator(ajax_required, name='dispatch')
class PluginDiagnoseView(
    UserIsInstructor,
    JSONFormResponseMixin,
    generic.DetailView
):
    """Show the diagnostics of a plugin that failed the verification tests."""

    model = models.Plugin
    template_name = 'dataops/includes/partial_diagnostics.html'
    msgs = None

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['diagnostic_table'] = self.msgs
        return context

    def get(self, request, *args, **kwargs) -> http.JsonResponse:
        plugin = self.get_object()
        try:
            p_instance, self.msgs = services.load_plugin(plugin.filename)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            return http.JsonResponse({
                'html_redirect': reverse('dataops:plugin_admin')})

        # If the new instance is now properly verified, simply redirect to the
        # transform page
        if p_instance:
            models.Plugin.objects.filter(
                id=kwargs['pk']).update(is_verified=True)
            return http.JsonResponse({
                'html_redirect': reverse('dataops:plugin_admin')})

        return super().get(request, *args, **kwargs)


@method_decorator(ajax_required, name='dispatch')
class PluginMoreInfoView(
    UserIsInstructor,
    JSONFormResponseMixin,
    generic.DetailView,
):

    model = models.Plugin
    template_name = 'dataops/includes/partial_plugin_long_description.html'

    p_instance = None
    
    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context['p_instance'] = self.p_instance
        return context

    def get(self, request, *args, **kwargs) -> http.JsonResponse:
        plugin = self.get_object()

        try:
            self.p_instance, __ = services.load_plugin(plugin.filename)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            return http.JsonResponse({
                'html_redirect': reverse('dataops:plugin_admin')})

        return super().get(request, *args, **kwargs)


@method_decorator(ajax_required, name='dispatch')
class PluginToggleView(
    UserIsAdmin,
    JSONFormResponseMixin,
    generic.DetailView,
):
    """Toggle the field is_enabled of a plugin."""

    model = models.Plugin
    http_method_names = ['post']

    def post(self, request, *args, **kwargs) -> http.JsonResponse:
        plugin_item = self.get_object()
        if plugin_item.is_verified:
            plugin_item.is_enabled = not plugin_item.is_enabled
            plugin_item.save(update_fields=['is_enabled'])
        return http.JsonResponse({'is_checked': plugin_item.is_enabled})
