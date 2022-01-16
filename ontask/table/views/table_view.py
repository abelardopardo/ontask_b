# -*- coding: utf-8 -*-

"""Functions to implement CRUD views for Views."""

from django import http
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, create_new_name, models
from ontask.condition.forms import FilterForm
from ontask.core import (
    JSONFormResponseMixin, SingleViewMixin, UserIsInstructor, ViewView,
    WorkflowView, ajax_required)
from ontask.table import forms, services


@method_decorator(ajax_required, name='dispatch')
class ViewAddView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.CreateView,
):
    """Create a new View."""

    http_method_names = ['get', 'post']
    form_class = forms.ViewAddForm
    template_name = 'table/includes/partial_view_add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'filter_form': FilterForm(
                self.request.POST or None,
                include_description=False)
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Catch if workflow is empty."""
        if self.workflow.nrows == 0:
            messages.error(
                request,
                _('Cannot add a view to a workflow without data'))
            return http.JsonResponse({'html_redirect': ''})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        filter_form = FilterForm(
            self.request.POST or None,
            include_description=False)
        if not filter_form.is_valid():
            # Second part of the form is not valid, reload.
            return self.get(self.request)

        if not form.has_changed() and not filter_form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = form.save(commit=False)
        filter_obj = filter_form.save(commit=False)

        services.save_view_form(
            self.request.user,
            self.workflow, view, filter_obj)
        # Propagate the save effect to M2M relations
        form.save_m2m()

        return http.JsonResponse({
            'html_redirect': reverse(
                'table:display_view',
                kwargs={'pk': view.id})})


@method_decorator(ajax_required, name='dispatch')
class ViewEditView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleViewMixin,
    ViewView,
    generic.UpdateView,
):
    """Update an existing View."""

    http_method_names = ['get', 'post']
    form_class = forms.ViewAddForm
    template_name = 'table/includes/partial_view_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'filter_form': FilterForm(
                self.request.POST or None,
                instance=self.table_view.filter,
                include_description=False)
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        filter_form = FilterForm(
            self.request.POST or None,
            instance=self.table_view.filter,
            include_description=False)
        if not filter_form.is_valid():
            # Second part of the form is not valid, reload.
            return self.get(self.request)

        if not form.has_changed() and not filter_form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        view = form.save(commit=False)
        filter_obj = filter_form.save(commit=False)

        services.save_view_form(
            self.request.user,
            self.workflow, view, filter_obj)
        # Propagate the save effect to M2M relations
        form.save_m2m()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ViewDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleViewMixin,
    ViewView,
    generic.DeleteView,
):
    """Delete a view."""

    template_name = 'table/includes/partial_view_delete.html'

    def delete(self, request, *args, **kwargs):
        self.table_view.log(request.user, models.Log.VIEW_DELETE)
        if self.table_view.filter:
            self.table_view.filter.delete_from_view()
        self.table_view.delete()
        return http.JsonResponse({'html_redirect': reverse('table:display')})


@method_decorator(ajax_required, name='dispatch')
class ViewCloneView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ViewView,
    generic.TemplateView,
):
    """Clone a view."""

    template_name = 'table/includes/partial_view_clone.html'

    def post(self, request, *args, **kwargs):
        try:
            new_view = services.do_clone_view(
                request.user,
                self.table_view,
                new_workflow=None,
                new_name=create_new_name(
                    self.table_view.name,
                    self.workflow.views))
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()
            return http.JsonResponse({'html_redirect': ''})

        return http.JsonResponse(
            {'html_redirect': reverse(
                'table:display_view',
                kwargs={'pk': new_view.id})})
