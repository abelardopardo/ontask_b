# -*- coding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from action import ops
from dataops.formula_evaluation import evaluate_node_sql, get_variables
from logs.models import Log
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
               'condition_id': condition_id,
               'add': is_new}

    # If the method is GET or the form is not valid, re-render the page.
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(template_name,
                                             context,
                                             request=request)
        return JsonResponse(data)

    # If the request has the 'action_content' field, update the action
    action_content = request.POST.get('action_content', None)
    if action_content:
        action.set_content(action_content)
        action.save()

    if is_filter:
        # Process the filter form
        # If this is a create filter operation, but the action has one,
        # flag the error
        if is_new and action.get_filter():
            # Should not happen. Go back to editing the action
            data['form_is_valid'] = True
            data['html_redirect'] = ''
            return JsonResponse(data)
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
                _('A condition with that name already exists in this action')
            )
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
                _('A column name with that name already exists.')
            )
            context = {'form': form,
                       'action_id': action.id,
                       'condition_id': condition_id,
                       'add': is_new}
            data['html_form'] = render_to_string(template_name,
                                                 context,
                                                 request=request)
            return JsonResponse(data)

        # New condition name does not collide with attribute names
        if form.cleaned_data['name'] in list(workflow.attributes.keys()):
            form.add_error(
                'name',
                _('The workflow has an attribute with this name.')
            )
            context = {'form': form,
                       'action_id': action.id,
                       'condition_id': condition_id,
                       'add': is_new}
            data['html_form'] = render_to_string(template_name,
                                                 context,
                                                 request=request)
            return JsonResponse(data)

        # If condition name has changed, rename appearances in the content
        # field of the action.
        if form.old_name and 'name' in form.changed_data:
            # Performing string substitution in the content and saving
            # TODO: Review!
            replacing = '{{% if {0} %}}'
            action.content = action.content.replace(
                replacing.format(form.old_name),
                replacing.format(condition.name))
            action.save()

    # Ok, here we can say that the data in the form is correct.
    data['form_is_valid'] = True

    # Proceed to update the DB
    if is_new:
        # Get the condition from the form, but don't commit as there are
        # changes pending.
        condition = form.save(commit=False)
        condition.action = action
        condition.is_filter = is_filter
        condition.save()
    else:
        condition = form.save()

    # Update the number of selected rows for the conditions
    condition.update_n_rows_selected()

    # Update the columns field
    condition.columns.set(
        action.workflow.columns.filter(
            name__in=get_variables(condition.formula))
    )

    # Update the condition
    condition.save()

    # Log the event
    formula, _ = evaluate_node_sql(condition.formula)
    if is_new:
        if is_filter:
            log_type = Log.FILTER_CREATE
        else:
            log_type = Log.CONDITION_CREATE
    else:
        if is_filter:
            log_type = Log.FILTER_UPDATE
        else:
            log_type = Log.CONDITION_UPDATE

    # Log the event
    Log.objects.register(request.user,
                         log_type,
                         condition.action.workflow,
                         {'id': condition.id,
                          'name': condition.name,
                          'selected_rows': condition.n_rows_selected,
                          'formula': formula})

    data['html_redirect'] = ''
    return JsonResponse(data)


class FilterCreateView(UserIsInstructor, generic.TemplateView):
    """
    CBV to create a filter through AJAX calls. It receives the action ID
    where the condition needs to be connected.
    """
    form_class = FilterForm
    template_name = 'action/includes/partial_filter_addedit.html'

    def get_context_data(self, **kwargs):
        context = super(FilterCreateView, self).get_context_data(**kwargs)
        context['add'] = True
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
    return save_condition_form(request,
                               form,
                               'action/includes/partial_filter_addedit.html',
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
        cond_filter = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=True
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        return redirect('workflow:index')

    data = dict()
    data['form_is_valid'] = False

    # Treat the two types of requests
    if request.method == 'POST':

        # If the request has 'action_content', update the action
        action_content = request.POST.get('action_content', None)
        if action_content:
            cond_filter.action.set_content(action_content)
            cond_filter.action.save()

        # Log the event
        formula, fields = evaluate_node_sql(cond_filter.formula)
        Log.objects.register(request.user,
                             Log.FILTER_DELETE,
                             cond_filter.action.workflow,
                             {'id': cond_filter.id,
                              'name': cond_filter.name,
                              'selected_rows': cond_filter.n_rows_selected,
                              'formula': formula,
                              'formula_fields': fields})

        # Get the action object for further processing
        action = cond_filter.action

        # Perform the delete operation
        cond_filter.delete()

        # Number of selected rows now needs to be updated in all remaining
        # conditions
        action.update_n_rows_selected()

        return JsonResponse({'form_is_valid': True, 'html_redirect': ''})

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
    template_name = 'action/includes/partial_condition_addedit.html'

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
                               'action/includes/partial_condition_addedit.html',
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
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content', None)
        if action_content:
            condition.action.set_content(action_content)
            condition.action.save()

        formula, fields = evaluate_node_sql(condition.formula)
        Log.objects.register(request.user,
                             Log.CONDITION_DELETE,
                             condition.action.workflow,
                             {'id': condition.id,
                              'name': condition.name,
                              'formula': formula,
                              'formula_fields': fields})

        # Perform the delete operation
        condition.delete()
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:edit',
                                        kwargs={'pk': condition.action.id})
        return JsonResponse(data)

    data['html_form'] = \
        render_to_string('action/includes/partial_condition_delete.html',
                         {'condition_id': condition.id},
                         request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def clone(request, pk):
    """
    JSON request to clone a condition. The post request must come with the action_content
    :param request: Request object
    :param pk: id of the condition to clone
    :return: JSON response
    """

    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('workflow:index')})

    # Get the condition
    try:
        condition = Condition.objects.filter(
            Q(action__workflow__user=request.user) |
            Q(action__workflow__shared=request.user),
            is_filter=False
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        messages.error(request,
                       _('Condition cannot be cloned.'))
        return JsonResponse({'html_redirect': reverse('action:index')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content', None)
    if action_content:
        condition.action.set_content(action_content)
        condition.action.save()

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
    Log.objects.register(request.user,
                         Log.CONDITION_CLONE,
                         condition.action.workflow,
                         {'id_old': old_id,
                          'id_new': condition.id,
                          'name_old': old_name,
                          'name_new': condition.name})

    messages.success(request,
                     _('Action successfully cloned.'))
    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})
