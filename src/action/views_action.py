# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.template import Context
from django.template import Template

from logs import ops
from ontask import is_instructor, decorators
from dataops import panda_db
from workflow.models import Workflow, get_column_names
from action.evaluate import evaluate_row

from .models import Action, Condition
from .forms import ActionForm, EditActionForm

# TODO: Action should be automatically saved, otherwise, when
# editing a condition, there is a warning and information may be
# lost.


def save_action_form(request, form, template_name, is_new):
    data = dict()
    # The form is false (thus needs to be rendered again, until proven
    # otherwise
    data['form_is_valid'] = False

    if request.method == 'POST':
        dst = request.POST['dst']
        workflow_id = request.session['ontask_workflow_id']
        if form.is_valid():
            action_item = form.save(commit=False)
            # Verify that that action does comply with the combined unique
            if is_new and Action.objects.filter(
                    workflow__user=request.user,
                    workflow__id=workflow_id,
                    name=action_item.name).exists():
                form.add_error('name',
                               'An action with that name already exists')
                data['html_redirect'] = reverse('action:index')
            else:
                # Correct action
                workflow = Workflow.objects.get(id=workflow_id)
                action_item.user = request.user
                action_item.workflow = workflow
                action_item.n_selected_rows = -1

                # Log the event
                if form.instance.pk:
                    ops.put(request.user,
                            'action_create',
                            {'id': action_item.id,
                             'workflow_id': workflow.id})
                else:
                    ops.put(request.user,
                            'action_update',
                            {'id': action_item.id,
                             'workflow_id': workflow.id})

                action_item.save()
                data['dst'] = dst
                # Ok, here we can say that the form is done.
                data['form_is_valid'] = True
                if dst == 'refresh':
                    actions = Action.objects.filter(
                        workflow__user=request.user,
                        workflow=workflow
                    )
                    data['html_item_list'] = \
                        render_to_string(
                            'action/includes/partial_action_list.html',
                            {'actions': actions})
                else:
                    data['html_redirect'] = reverse(
                        'action:edit', kwargs={'pk': action_item.id}
                    )
    else:
        dst = request.GET['dst']

    context = {'form': form, 'dst': dst}
    data['html_form'] = render_to_string(template_name,
                                         context,
                                         request=request)
    return JsonResponse(data)


def preview_response(request, pk, template, prelude=None):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :return:
    """

    # Action being used
    action = get_object_or_404(Action, id=pk)

    # Get the workflow to obtain row numbers
    workflow = Workflow.objects.get(pk=action.workflow.id)

    # To include in the JSON response
    data = dict()

    # Get the index parameter or zero if anything goes wrong
    try:
        idx = int(request.GET.get('idx', 1))
    except Exception:
        idx = 1

    # Get the total number of items
    n_items = action.n_selected_rows
    if n_items == -1:
        n_items = workflow.nrows

    # Set the idx to a legal value just in case
    if not 1 <= idx <= n_items:
        idx = 1

    prv = idx - 1
    if prv <= 0:
        prv = n_items

    nxt = idx + 1
    if nxt > n_items:
        nxt = 1

    action_content = evaluate_row(action, idx)
    if action_content is None:
        action_content = \
            "Error while retrieving content for row {0}".format(idx)

    data['html_form'] = \
        render_to_string(template,
                         {'action': action,
                          'action_content': action_content,
                          'index': idx,
                          'nxt': nxt,
                          'prv': prv,
                          'prelude': prelude},
                         request=request)

    return JsonResponse(data)


@method_decorator(decorators, name='dispatch')
class IndexView(generic.ListView):
    template_name = 'action/index.html'
    context_object_name = 'actions'

    def get_queryset(self):
        workflow_id = self.request.session.get('ontask_workflow_id', None)
        return Action.objects.filter(workflow__user=self.request.user,
                                     workflow__id=workflow_id)


@method_decorator(decorators, name='dispatch')
class ActionCreateView(generic.TemplateView):
    form_class = ActionForm
    template_name = 'action/includes/partial_action_create.html'

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        context['dst'] = self.request.GET['dst']
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_action_form(request, form, self.template_name, True)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        return save_action_form(request, form, self.template_name, True)


@login_required
@user_passes_test(is_instructor)
def delete_action(request, pk):
    action = get_object_or_404(Action, pk=pk, workflow__user=request.user)
    data = dict()
    if request.method == 'POST':
        # Set the destination to be used in the JS for last action
        dst = request.POST['dst']
        data['dst'] = dst

        # Log the event
        ops.put(request.user,
                'action_delete',
                {'id': action.id,
                 'workflow_id': action.workflow.id})

        # Perform the delete operation
        action.delete()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True

        if dst == 'refresh':
            workflow = Workflow.objects.get(
                user=request.user,
                id=request.session['ontask_workflow_id'])
            # Create the html_item_list to refresh
            actions = Action.objects.filter(
                workflow__user=request.user,
                workflow=workflow
            )
            data['html_item_list'] = \
                render_to_string('action/includes/partial_action_list.html',
                                 {'actions': actions})
        else:  # dst = redirect
            data['html_redirect'] = reverse('action:index')

    else:
        data['html_form'] = \
            render_to_string('action/includes/partial_action_delete.html',
                             {'action': action,
                              'dst': request.GET['dst']},
                             request=request)
    return JsonResponse(data)


@login_required
@user_passes_test(is_instructor)
def edit_action(request, pk):
    # Get the action and create the form
    action = get_object_or_404(Action, pk=pk, workflow__user=request.user)
    workflow = get_object_or_404(Workflow, pk=action.workflow.id)

    form = EditActionForm(request.POST or None, instance=action)

    # See if the action has a filter or not
    try:
        filter_condition = Condition.objects.get(action=action,
                                                 is_filter=True)
    except Condition.DoesNotExist:
        filter_condition = None

    # Conditions to show in the page as well.
    conditions = Condition.objects.filter(action=action,
                                          is_filter=False)

    column_names = get_column_names(workflow)

    # Boolean to find out if there is a matrix attached to this workflow
    has_data = panda_db.workflow_has_matrix(action.workflow)

    # Get the total number of rows in DF and those selected by filter.
    total_rows = workflow.nrows
    selected_rows = action.n_selected_rows

    # if filter_condition:

    # Attributes available from the workflow
    attribute_names = None
    if workflow.attributes != '':
        attribute_names = [x for x in json.loads(workflow.attributes).keys()]

    context = {'filter_condition': filter_condition,
               'action': action,
               'conditions': conditions,
               'query_builder_ops': workflow.query_builder_ops,
               'attribute_names': attribute_names,
               'column_names': column_names,
               'selected_rows': selected_rows,
               'has_data': has_data,
               'total_rows': total_rows,
               'form': form}

    # Processing the request after receiving the text from tinyMCE!!
    if request.method == 'POST':
        # Get the next step
        next_step = request.POST['Submit']

        if form.is_valid():
            content = form.cleaned_data.get('content', None)

            # Render the content as a template and catch potential problems
            try:
                template = Template(content)
                tplt_context = Context({'myname': 'Abelardo', 'cond': True})
                content_result = template.render(tplt_context)
            except Exception, e:
                form.add_error(None, e.message)
                return render(request, 'action/edit.html', context)

            # Log the event
            ops.put(request.user,
                    'action_edit',
                    {'id': action.id,
                     'content': content})

            # Text is good. Update the content of the action
            action.content = content
            action.save()

            # Closing
            if next_step == 'Save-and-close':
                return redirect(reverse('action:index'))

    # Return the same form in the same page
    return render(request, 'action/edit.html', context=context)


@login_required
@user_passes_test(is_instructor)
def preview(request, pk):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :return:
    """

    return preview_response(request,
                            pk,
                            'action/includes/partial_action_preview.html')
