# -*- coding: utf-8 -*-

"""Functions for Condition CRUD."""

from django import http
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import create_new_name, models
from ontask.condition import forms, services, services as condition_services
from ontask.core import (
    ActionView, ConditionView, JSONFormResponseMixin, UserIsInstructor,
    ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ConditionCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView
):
    """Class to create a condition or filter."""
    form_class = None
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        # Set the action object
        self.object = self.get_object()
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.object.set_text_content(action_content)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.object
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(self.request, form, self.object)


@method_decorator(ajax_required, name='dispatch')
class ConditionUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ConditionView,
    generic.UpdateView
):
    """Process the Condition update view."""

    form_class = forms.ConditionForm
    template_name = 'condition/includes/partial_condition_addedit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.object.action
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            self.request,
            form,
            self.object.action)


@method_decorator(ajax_required, name='dispatch')
class FilterUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView,
):
    """Process the filter update view."""

    http_method_names = ['get', 'post']
    form_class = forms.FilterForm
    template_name = 'condition/includes/partial_filter_addedit.html'
    filter = None

    def dispatch(self, request, *args, **kwargs):
        """Set the object/action and see if there is content to update."""
        self.object = self.get_object()

        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.object.set_text_content(action_content)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.object
        kwargs['instance'] = self.filter
        return kwargs

    def get(self, request, *args, **kwargs):
        """Verify that action and filter are correct."""
        self.filter = self.object.filter
        if self.filter is None:
            return http.JsonResponse({'html_redirect': None})

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            self.request,
            form,
            self.object)


@method_decorator(ajax_required, name='dispatch')
class FilterSetView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Set the formula in the view as the action filter."""

    http_method_names = ['get']
    wf_pf_related = 'views'

    def get(self, request, *args, **kwargs):
        action = self.get_object()
        view = self.workflow.views.filter(pk=kwargs['view_id']).first()
        if not view or not view.filter:
            messages.error(
                request,
                _('Incorrect invocation of set view as filter'),
            )
            return http.JsonResponse({'html_redirect': ''})

        # If the action has a filter nuke it.
        action.filter = view.filter
        action.rows_all_false = None
        action.save(update_fields=['filter', 'rows_all_false'])

        # Row counts need to be updated.
        action.update_selected_row_counts()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConditionDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ConditionView,
    generic.DeleteView,
):
    """Delete a condition."""

    http_method_names = ['get', 'post']
    template_name = 'condition/includes/partial_condition_delete.html'
    s_related = 'action'

    def delete(self, request, *args, **kwargs):
        condition = self.get_object()
        action = condition.action
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            action.set_text_content(action_content)

        condition.log(request.user, models.Log.CONDITION_DELETE)
        condition.delete()
        action.rows_all_false = None
        action.save(update_fields=['rows_all_false'])
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class FilterDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.TemplateView,
):
    """Delete the filter in the action."""

    http_method_names = ['get', 'post']
    template_name = 'condition/includes/partial_filter_delete.html'
    s_related = 'filter'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        filter_obj = self.object.filter
        if filter_obj is None:
            return http.JsonResponse({'html_redirect': ''})

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        filter_obj = action.filter

        filter_obj.log(request.user, models.Log.CONDITION_DELETE)
        filter_obj.delete_from_action()

        action.filter = None
        action.rows_all_false = None
        action.save(update_fields=['filter', 'rows_all_false'])

        action.update_selected_row_counts()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConditionCloneView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ConditionView,
    generic.DetailView
):
    """Process the Clone condition view."""

    model = models.Condition
    http_method_names = 'post'
    wf_pf_related = 'actions'
    s_related = 'action'

    def post(self, request, *args, **kwargs):
        condition = self.get_object()
        action_pk = kwargs.get('action_pk')
        if action_pk:
            action = self.workflow.actions.filter(
                id=action_pk).prefetch_related('conditions').first()
            if not action:
                messages.error(request, _('Incorrect action id.'))
                return http.JsonResponse({'html_redirect': ''})
        else:
            action = condition.action

        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content and action:
            condition.action.set_text_content(action_content)

        condition_services.do_clone_condition(
            request.user,
            condition,
            new_action=action,
            new_name=create_new_name(condition.name, action.conditions))

        messages.success(request, _('Condition successfully cloned.'))

        return http.JsonResponse({'html_redirect': ''})
