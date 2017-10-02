# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator

from ontask import is_instructor, decorators
from logs import ops
from dataops.panda_db import evaluate_node
from .models import Action, Condition
from .forms import ConditionForm

from dataops import panda_db


def save_condition_form(request, form, template_name, action_id, condition,
                        is_new, is_filter):
    # Get the action object
    action = get_object_or_404(Action, id=action_id)

    # Get the condition id to be included in the context
    if condition is None:
        condition_id = -1
    else:
        condition_id = condition.id

    data = dict()
    # The form is false (thus needs to be rendered again, until proven
    # otherwise
    data['form_is_valid'] = False

    if request.method == 'POST':
        dst = request.POST['dst']
        if form.is_valid():
            condition_item = form.save(commit=False)
            # Verify that that workflow does comply with the combined unique
            if is_new and Condition.objects.filter(
                    action__workflow__user=request.user,
                    action=action,
                    name=condition_item.name).exists():
                form.add_error('name',
                               'A condition with that name already exists')
            else:
                # Ok, here we can say that the form is done.
                data['form_is_valid'] = True

                # Correct Filter
                condition_item.action = action
                condition_item.is_filter = is_filter
                # New filter, update the number of rows in the action
                if is_filter:
                    action.n_selected_rows = \
                        panda_db.num_rows(action.workflow.id,
                                          json.loads(condition_item.formula))
                    action.save()
                    log_type = 'filter'
                else:
                    action.n_selected_rows = -1
                    log_type = 'condition'

                # Save the condition/filter
                condition_item.save()

                # Log the event
                formula = evaluate_node(json.loads(condition_item.formula),
                                                   None,
                                                   'sql')
                if is_new:
                    # Log the event
                    ops.put(request.user,
                            log_type + '_create',
                            condition_item.action.workflow,
                            {'id': condition_item.id,
                             'name': condition_item.name,
                             'selected_rows': action.n_selected_rows,
                             'formula': formula})
                else:
                    ops.put(request.user,
                            log_type + '_update',
                            condition_item.action.workflow,
                            {'id': condition_item.id,
                             'name': condition_item.name,
                             'selected_rows': action.n_selected_rows,
                             'formula': formula})

                data['dst'] = 'redirect'
                data['html_redirect'] = reverse('action:edit',
                                                kwargs={'pk': action.id})
    else:
        dst = request.GET['dst']

    context = {'form': form,
               'dst': dst,
               'action_id': action.id,
               'condition_id': condition_id}
    data['html_form'] = render_to_string(template_name,
                                         context,
                                         request=request)
    return JsonResponse(data)


@method_decorator(decorators, name='dispatch')
class FilterCreateView(generic.TemplateView):
    form_class = ConditionForm
    template_name = 'action/includes/partial_filter_create.html'

    def get_context_data(self, **kwargs):
        context = super(FilterCreateView, self).get_context_data(**kwargs)
        context['dst'] = self.request.GET['dst']
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_condition_form(request, form, self.template_name,
                                   kwargs['pk'], None, True, True)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        return save_condition_form(request, form, self.template_name,
                                   kwargs['pk'], None, True, True)  # It is new


@login_required
@user_passes_test(is_instructor)
def edit_filter(request, pk):
    # Get the action, and then its filter
    filter = get_object_or_404(Condition,
                               action__id=pk,
                               action__workflow__user=request.user,
                               is_filter=True)

    form = ConditionForm(request.POST or None, instance=filter)

    # Render the form with the Condition information
    return save_condition_form(request, form,
                               'action/includes/partial_filter_edit.html',
                               filter.action.id, filter, False,
                               True)  # It is not new


@login_required
@user_passes_test(is_instructor)
def delete_filter(request, pk):
    # Get the action, and then its filter
    filter = get_object_or_404(Condition,
                               action__id=pk,
                               action__workflow__user=request.user,
                               is_filter=True)

    data = dict()
    data['form_is_valid'] = False
    data['dst'] = 'redirect'

    # Treat the two types of requests
    if request.method == 'POST':

        # Log the event
        formula = evaluate_node(json.loads(filter.formula), None, 'sql')
        ops.put(request.user,
                'filter_delete',
                filter.action.workflow,
                {'id': filter.id,
                 'name': filter.name,
                 'selected_rows': filter.action.n_selected_rows,
                 'formula': formula})

        # Perform the delete operation
        filter.delete()

        # Action now has number of selected rows equal to 0
        action = Action.objects.get(pk=filter.action.id)
        action.n_selected_rows = -1
        action.save()

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:edit',
                                        args=[filter.action.id])
    else:
        data['html_form'] = \
            render_to_string('action/includes/partial_filter_delete.html',
                             {'action': filter.action,
                              'dst': request.GET['dst']},
                             request=request)

    return JsonResponse(data)


@method_decorator(decorators, name='dispatch')
class ConditionCreateView(generic.TemplateView):
    form_class = ConditionForm
    template_name = 'action/includes/partial_condition_create.html'

    def get_context_data(self, **kwargs):
        context = super(ConditionCreateView, self).get_context_data(**kwargs)
        context['dst'] = self.request.GET['dst']
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_condition_form(request, form, self.template_name,
                                   kwargs['pk'], None, True, True)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        return save_condition_form(request, form, self.template_name,
                                   kwargs['pk'], None, True, False)  # It is new


@login_required
@user_passes_test(is_instructor)
def edit_condition(request, pk):
    # Get the action
    condition = get_object_or_404(Condition,
                                  id=pk,
                                  action__workflow__user=request.user,
                                  is_filter=False)

    form = ConditionForm(request.POST or None, instance=condition)

    # Render the form with the Condition information
    return save_condition_form(request, form,
                               'action/includes/partial_condition_edit.html',
                               condition.action.id, condition, False,
                               False)  # It is not new


@login_required
@user_passes_test(is_instructor)
def delete_condition(request, pk):
    # Get the action
    condition = get_object_or_404(Condition,
                                  id=pk,
                                  action__workflow__user=request.user,
                                  is_filter=False)

    data = dict()
    data['form_is_valid'] = False
    data['dst'] = 'redirect'

    # Treat the two types of requests
    if request.method == 'POST':

        formula = evaluate_node(json.loads(condition.formula), None, 'sql')
        ops.put(request.user,
                'condition_delete',
                condition.action.workflow,
                {'id': condition.id,
                 'name': condition.name,
                 'formula': formula})

        # Perform the delete operation
        condition.delete()
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:edit',
                                        args=[condition.action.id])
    else:
        data['html_form'] = \
            render_to_string('action/includes/partial_condition_delete.html',
                             {'condition': condition,
                              'dst': request.GET['dst']},
                             request=request)

    return JsonResponse(data)
