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
    ActionView, ConditionView, JSONFormResponseMixin,
    SingleConditionMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ConditionCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.CreateView
):
    """Class to create a condition or filter."""
    form_class = None
    template_name = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.action
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(self.request, form, self.action)


@method_decorator(ajax_required, name='dispatch')
class ConditionUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleConditionMixin,
    ConditionView,
    generic.UpdateView
):
    """Process the Condition update view."""

    form_class = forms.ConditionForm
    template_name = 'condition/includes/partial_condition_addedit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.condition.action
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            self.request,
            form,
            self.condition.action)


@method_decorator(ajax_required, name='dispatch')
class FilterUpdateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView,
):
    """Process the filter update view."""

    form_class = forms.FilterForm
    template_name = 'condition/includes/partial_filter_addedit.html'
    filter = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.action
        kwargs['instance'] = self.filter
        return kwargs

    def get(self, request, *args, **kwargs):
        self.filter = self.action.filter
        if self.filter is None:
            return http.JsonResponse({'html_redirect': None})

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            self.request,
            form,
            self.action)


@method_decorator(ajax_required, name='dispatch')
class FilterSetView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Set the formula in the view as the action filter."""

    def get(self, request, *args, **kwargs):
        view = self.workflow.views.filter(pk=kwargs['view_id']).first()
        if not view or not view.filter:
            messages.error(
                request,
                _('Incorrect invocation of set view as filter'),
            )
            return http.JsonResponse({'html_redirect': ''})

        # If the action has a filter nuke it.
        self.action.filter = view.filter
        self.action.rows_all_false = None
        self.action.save(update_fields=['filter', 'rows_all_false'])

        # Row counts need to be updated.
        self.action.update_selected_row_counts()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ConditionDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleConditionMixin,
    ConditionView,
    generic.DeleteView,
):
    """Delete a condition."""

    template_name = 'condition/includes/partial_condition_delete.html'

    def delete(self, request, *args, **kwargs):
        action = self.condition.action
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            action.set_text_content(action_content)

        self.condition.log(request.user, models.Log.CONDITION_DELETE)
        self.condition.delete()
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

    def get(self, request, *args, **kwargs):
        filter_obj = self.action.filter
        if filter_obj is None:
            return http.JsonResponse({'html_redirect': ''})

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # If the request has 'action_content', update the action
        filter_obj = self.action.filter
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)

        filter_obj.log(request.user, models.Log.CONDITION_DELETE)
        filter_obj.delete_from_action()

        self.action.filter = None
        self.action.rows_all_false = None
        self.action.save(update_fields=['filter', 'rows_all_false'])

        self.action.update_selected_row_counts()

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

    def post(self, request, *args, **kwargs):
        action_pk = kwargs.get('action_pk')
        if action_pk:
            action = self.workflow.actions.filter(id=action_pk).first()
            if not action:
                messages.error(request, _('Incorrect action id.'))
                return http.JsonResponse({'html_redirect': ''})
        else:
            action = self.condition.action

        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content and action:
            self.condition.action.set_text_content(action_content)

        condition_services.do_clone_condition(
            request.user,
            self.condition,
            new_action=action,
            new_name=create_new_name(self.condition.name, action.conditions))

        messages.success(request, _('Condition successfully cloned.'))

        return http.JsonResponse({'html_redirect': ''})
