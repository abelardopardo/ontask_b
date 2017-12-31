# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.views import generic

import logs
import logs.ops
from action import ops
from dataops import pandas_db
from dataops.formula_evaluation import evaluate_node_sql
from ontask.permissions import is_instructor, UserIsInstructor
from workflow.ops import get_workflow
from .forms import ConditionForm, FilterForm
from .models import Action, Condition


def save_condition_form(request,
                        form,
                        template_name,
                        action,
                        condition,
                        is_filter):
    """
    Function to process the AJAX form to create and update conditions and
    filters.
    :param request: HTTP request
    :param form: Form being used to ask for the fields
    :param template_name: Template being used to render the form
    :param action: The action to which the condition is attached to
    :param condition: Condition object being manipulated or None if creating
    :param is_filter: The condition is a filter
    :return:
    """
    # Ajax response
    data = dict()

    # In principle we re-render until proven otherwise
    data['form_is_valid'] = False

    # The condition is new if no value is given
    is_new = condition is None

    if is_new:
        condition_id = -1
    else:
        condition_id = condition.id

    # Context for rendering
    context = {'form': form,
               'action_id': action.id,
               'condition_id': condition_id}

    # If the method is GET or the form is not valid, re-render the page.
    if request.method == 'GET' or not form.is_valid():

        # If the request has the 'action_content' field, update the action
        action_content = request.GET.get('action_content', None)
        if action_content:
            action.content = action_content
            action.save()

        data['html_form'] = render_to_string(template_name,
                                             context,
                                             request=request)
        return JsonResponse(data)

    if is_filter:
        # Process the filter form
        # If this is a create filter operation, but the action has one,
        # flag the error
        if is_new and Condition.objects.filter(action=action,
                                               is_filter=True).exists():
            # Should not happen. Go back to editing the action
            data['form_is_valid'] = True
            data['html_redirect'] = reverse('action:edit_out',
                                            kwargs={'pk': action.id})
            return JsonResponse(data)

        log_type = 'filter'
    else:
        # Verify that the condition name does not exist yet (Uniqueness FIX)
        qs = Condition.objects.filter(
            name=form.cleaned_data['name'],
            action=action,
            is_filter=False)
        if (is_new and qs.exists()) or \
                (not is_new and qs.filter(~Q(id=condition_id)).exists()):
            form.add_error(
                'name',
                'A condition with that name already exists in this action')
            data['html_form'] = render_to_string(template_name,
                                                 context,
                                                 request=request)
            return JsonResponse(data)
        # Verify that the condition name does not collide with column names
        workflow = get_workflow(request, action.workflow.id)
        if not workflow:
            # Workflow is not accessible. Go back to the index.
            data['form_is_valid'] = True
            data['html_redirect'] = reverse('workflow:index')
            return JsonResponse(data)

        # New condition name does not collide with column name
        if form.cleaned_data['name'] in workflow.get_column_names():
            form.add_error(
                'name',
                'A column name with that name already exists.')
            context = {'form': form,
                       'action_id': action.id,
                       'condition_id': condition_id}
            data['html_form'] = render_to_string(template_name,
                                                 context,
                                                 request=request)
            return JsonResponse(data)

        # New condition name does not collide with attribute names
        if form.cleaned_data['name'] in workflow.attributes.keys():
            form.add_error(
                'name',
                'The workflow has an attribute with this name.')
            context = {'form': form,
                       'action_id': action.id,
                       'condition_id': condition_id}
            data['html_form'] = render_to_string(template_name,
                                                 context,
                                                 request=request)
            return JsonResponse(data)

        # If condition name has changed, rename appearances in the content
        # field of the action.
        if form.old_name and 'name' in form.changed_data:
            # Performing string substitution in the content and saving
            replacing = '{{% if {0} %}}'
            action.content = action.content.replace(
                replacing.format(form.old_name),
                replacing.format(condition.name))
            action.save()

        log_type = 'condition'

    # Ok, here we can say that the data in the form is correct.
    data['form_is_valid'] = True

    # Proceed to update the DB
    if is_new:
        # Update the fields not in the form

        # Get the condition from the form, but don't commit as there are
        # changes pending.
        condition = form.save(commit=False)

        condition.action = action
        condition.is_filter = is_filter
        condition.save()
    else:
        condition = form.save()

    if is_filter:
        # Update the number of selected rows applying the new formula
        action.n_selected_rows = \
            pandas_db.num_rows(action.workflow.id, condition.formula)

    # Update the action
    action.save()

    # Log the event
    formula, _ = evaluate_node_sql(condition.formula)
    if is_new:
        log_type += '_create'
    else:
        log_type += '_update'

    # Log the event
    logs.ops.put(request.user,
                 log_type,
                 condition.action.workflow,
                 {'id': condition.id,
                  'name': condition.name,
                  'selected_rows': action.n_selected_rows,
                  'formula': formula})

    data['html_redirect'] = reverse('action:edit_out', kwargs={'pk': action.id})
    return JsonResponse(data)


class FilterCreateView(UserIsInstructor, generic.TemplateView):
    """
    CBV to create a filter through AJAX calls. It receives the action ID
    where the condition needs to be connected.
    """
    form_class = FilterForm
    template_name = 'action/includes/partial_filter_create.html'

    def get_context_data(self, **kwargs):
        context = super(FilterCreateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        # Get the action that is being used
        try:
            action = Action.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().get(pk=kwargs['pk'])
        except (KeyError, ObjectDoesNotExist):
            return redirect('workflow:index')

        form = self.form_class()
        return save_condition_form(request,
                                   form,
                                   self.template_name,
                                   action,
                                   None,  # no current condition object
                                   True)  # Is Filter

    def post(self, request, *args, **kwargs):
        del args
        # Get the action that is being used
        try:
            action = Action.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().get(pk=kwargs['pk'])
        except (KeyError, ObjectDoesNotExist):
            return redirect('workflow:index')

        form = self.form_class(request.POST)
        return save_condition_form(request,
                                   form,
                                   self.template_name,
                                   action,
                                   None,  # No current condition object
                                   True)  # Is Filter


@user_passes_test(is_instructor)
def edit_filter(request, pk):
    """
    Edit the filter of an action through AJAX.
    :param request: HTTP request
    :param pk: condition ID
    :return: AJAX response
    """
    # Get the filter
    try:
        cond_filter = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=True
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        return redirect('workflow:index')

    # Create the filter and populate with existing data
    form = FilterForm(request.POST or None, instance=cond_filter)

    # Render the form with the Condition information
    return save_condition_form(request, form,
                               'action/includes/partial_filter_edit.html',
                               cond_filter.action,
                               cond_filter,  # Condition object
                               True)  # It is a filter


@user_passes_test(is_instructor)
def delete_filter(request, pk):
    """
    Handle the AJAX request to delete a filter
    :param request: AJAX request
    :param pk: Filter ID
    :return: AJAX response
    """
    # Get the filter
    try:
        cond_filter = Condition.objects.get(
            pk=pk,
            action__workflow__user=request.user,
            is_filter=True
        )
    except (KeyError, ObjectDoesNotExist):
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False

    # Treat the two types of requests
    if request.method == 'POST':
        # Log the event
        formula, fields = evaluate_node_sql(cond_filter.formula)
        logs.ops.put(request.user,
                     'filter_delete',
                     cond_filter.action.workflow,
                     {'id': cond_filter.id,
                      'name': cond_filter.name,
                      'selected_rows': cond_filter.action.n_selected_rows,
                      'formula': formula,
                      'formula_fields': fields}, )

        # Perform the delete operation
        cond_filter.delete()

        # Action now has number of selected rows equal to 0
        action = Action.objects.get(pk=cond_filter.action.id)
        action.n_selected_rows = -1
        action.save()

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:edit_out',
                                        kwargs={'pk': cond_filter.action.id})
        return JsonResponse(data)

    # If the request has the 'action_content', update the action
    action_content = request.GET.get('action_content', None)
    if action_content:
        cond_filter.action.content = action_content
        cond_filter.action.save()

    data['html_form'] = \
        render_to_string('action/includes/partial_filter_delete.html',
                         {'id': cond_filter.id},
                         request=request)

    return JsonResponse(data)


class ConditionCreateView(UserIsInstructor, generic.TemplateView):
    """
    CBV to handle the AJAX request to create a non-filter condition. The PK
    is the action id where the condition needs to point.
    """
    form_class = ConditionForm
    template_name = 'action/includes/partial_condition_create.html'

    def get_context_data(self, **kwargs):
        context = super(ConditionCreateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        # Get the action that is being used
        try:
            action = Action.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().get(pk=kwargs['pk'])
        except (KeyError, ObjectDoesNotExist):
            return redirect('workflow:index')

        form = self.form_class()
        return save_condition_form(request,
                                   form,
                                   self.template_name,
                                   action,
                                   None,
                                   False)  # Is it a filter?

    def post(self, request, *args, **kwargs):
        del args
        # Get the action that is being used
        try:
            action = Action.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().get(pk=kwargs['pk'])
        except (KeyError, ObjectDoesNotExist):
            return redirect('workflow:index')

        form = self.form_class(request.POST)

        return save_condition_form(request,
                                   form,
                                   self.template_name,
                                   action,
                                   None,
                                   False)  # It is not a filter


@user_passes_test(is_instructor)
def edit_condition(request, pk):
    """
    Handle the AJAX request to edit a condition. PK is the condition ID
    :param request: AJAX request
    :param pk: Condition ID
    :return: AJAX reponse
    """
    # Get the condition
    try:
        condition = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=False
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('workflow:index')})

    form = ConditionForm(request.POST or None, instance=condition)

    # Render the form with the Condition information
    return save_condition_form(request, form,
                               'action/includes/partial_condition_edit.html',
                               condition.action,
                               condition,
                               False)  # It is not new


@user_passes_test(is_instructor)
def delete_condition(request, pk):
    """
    Handle the AJAX request to delete a condition. The pk is the condition ID.
    :param request: HTTP request
    :param pk: condition or filter id
    :return: AJAX response to render
    """
    # AJAX result
    data = {}

    # Get the condition
    try:
        condition = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=False
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data = {'form_is_valid': False}

    # Treat the two types of requests
    if request.method == 'POST':
        formula, fields = evaluate_node_sql(condition.formula)
        logs.ops.put(request.user,
                     'condition_delete',
                     condition.action.workflow,
                     {'id': condition.id,
                      'name': condition.name,
                      'formula': formula,
                      'formula_fields': fields})

        # Perform the delete operation
        condition.delete()
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:edit_out',
                                        kwargs={'pk': condition.action.id})
        return JsonResponse(data)

    # If the request has the 'action_content', update the action
    action_content = request.GET.get('action_content', None)
    if action_content:
        condition.action.content = action_content
        condition.action.save()

    data['html_form'] = \
        render_to_string('action/includes/partial_condition_delete.html',
                         {'condition_id': condition.id},
                         request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def clone(request, pk):
    """
    View to clone an action
    :param request: Request object
    :param pk: id of the condition to clone
    :return:
    """

    # Get the condition
    try:
        condition = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=False
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        messages.error(request,
                       'Condition cannot be cloned.')
        return redirect(reverse('action:index'))

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + condition.name
    while Condition.objects.filter(name=new_name,
                                   action=condition.action).exists():
        new_name = 'Copy of ' + new_name

    old_id = condition.id
    old_name = condition.name
    condition = ops.clone_condition(condition,
                                    new_action=None,
                                    new_name=new_name)

    # Log event
    logs.ops.put(request.user,
                 'condition_clone',
                 condition.action.workflow,
                 {'id_old': old_id,
                  'id_new': condition.id,
                  'name_old': old_name,
                  'name_new': condition.name})

    messages.success(request,
                     'Action successfully cloned.')
    return redirect(reverse('action:edit_out',
                            kwargs={'pk': condition.action.id}))
