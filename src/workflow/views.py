# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django_tables2 import RequestConfig
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework import generics


from rest_framework.response import Response

from rest_framework import permissions

from action.models import Condition
from dataops import panda_db
from logs import ops
from ontask import is_instructor, decorators
from .forms import WorkflowForm, AttributeForm, AttributeItemForm
from .models import Workflow
from .serializers import WorkflowSerializer

class OperationsColumn(tables.Column):

    empty_values = []

    def __init__(self, *args, **kwargs):
        super(OperationsColumn, self).__init__(*args, **kwargs)
        self.attrs = {'th': {'style': 'text-align:center;'},
                      'td': {'style': 'text-align:center;'}}
        self.orderable = False

    def render(self, record):
        return render_to_string(
            'workflow/includes/partial_workflow_operations.html',
            {'id': record.id})


class WorkflowTable(tables.Table):

    name = tables.Column(
        attrs={'th': {'style': 'text-align:center;vertical-align:middle;'},
               'td': {'style': 'text-align:center;vertical-align:middle;'}},
        verbose_name=str('Name')
    )

    created = tables.DateTimeColumn(
        attrs={'th': {'style': 'text-align:center;vertical-align:middle;'},
               'td': {'style': 'text-align:center;vertical-align:middle;'}},
        verbose_name='Created'

    )

    description_text = tables.Column(
        attrs={'th': {'style': 'text-align:center;vertical-align:middle;'},
               'td': {'style': 'text-align:center;vertical-align:middle;'}},
        verbose_name=str('Description')
    )

    operations = OperationsColumn(
        attrs={'th': {'style': 'text-align:center;vertical-align:middle;'},
               'td': {'style': 'text-align:center;vertical-align:middle;'}},
        verbose_name='Operations',
        orderable=False
    )

    def render_name(self, record):
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('workflow:detail', kwargs={'pk': record.id}),
                record.name
            )
        )

    class Meta:
        model = Workflow
        fields = ('name', 'description_text', 'created')
        sequence = ('name', 'description_text', 'created')
        exclude = ('id', 'user', 'attributes', 'nrows', 'ncols', 'column_names',
                   'column_types', 'column_unique', 'query_builder_ops',
                   'data_frame_table_name')

        attrs = {
            'class': 'table table-stripped table-bordered table-hover',
            'id': 'item-table'
        }

        row_attrs = {
            'style': 'text-align:center;'
        }

        # class="text-center bg-warning"'No workflows'
        empty_text = 'No workflows'


def save_workflow_form(request, form, template_name, is_new):
    data = dict()
    # The form is false (thu s needs to be rendered again, until proven
    # otherwise
    data['form_is_valid'] = False

    if request.method == 'POST':
        dst = request.POST['dst']
        if form.is_valid():
            workflow_item = form.save(commit=False)
            # Verify that that workflow does comply with the combined unique
            if is_new and Workflow.objects.filter(
                    user=request.user, name=workflow_item.name).exists():
                form.add_error('name',
                               'A workflow with that name already exists')
                data['html_redirect'] = reverse('workflow:index')
            else:

                # Correct workflow
                workflow_item.user = request.user
                workflow_item.nrows = 0
                workflow_item.ncols = 0
                is_new = form.instance.pk is None
                # Save the workflow
                workflow_item.save()

                # Log event
                if is_new:
                    ops.put(request.user,
                            'workflow_create',
                            workflow_item,
                            {'id': workflow_item.id,
                             'name': workflow_item.name})
                else:
                    ops.put(request.user,
                            'workflow_update',
                            workflow_item,
                            {'id': workflow_item.id,
                             'name': workflow_item.name})

                data['dst'] = dst
                # Ok, here we can say that the form is done.
                data['form_is_valid'] = True
                if dst == 'refresh':
                    workflows = Workflow.objects.filter(user=request.user)
                    table = WorkflowTable(workflows)
                    data['html_item_list'] = table.as_html(request)
    else:
        dst = request.GET['dst']

    context = {'form': form, 'dst': dst}
    data['html_form'] = render_to_string(template_name,
                                         context,
                                         request=request)
    return JsonResponse(data)


@login_required
@user_passes_test(is_instructor)
def workflow_index(request):
    request.session.pop('ontask_workflow_id', None)
    request.session.pop('ontask_workflow_name', None)
    workflows = Workflow.objects.filter(user=request.user)
    table = WorkflowTable(workflows)
    RequestConfig(request,
                  paginate={'per_page': 15}).configure(table)

    return render(request, 'workflow/index.html', {'table': table})


@method_decorator(decorators, name='dispatch')
class WorkflowCreateView(generic.TemplateView):
    form_class = WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_context_data(self, **kwargs):
        context = super(WorkflowCreateView, self).get_context_data(**kwargs)
        context['dst'] = self.request.GET['dst']
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_workflow_form(request, form, self.template_name, True)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        return save_workflow_form(request, form, self.template_name, True)


@login_required
@user_passes_test(is_instructor)
def update(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    form = WorkflowForm(request.POST or None, instance=workflow)

    return save_workflow_form(request,
                              form,
                              'workflow/includes/partial_workflow_update.html',
                              False)


@login_required
@user_passes_test(is_instructor)
def flush(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    data = dict()
    # This form will always redirect
    data['dst'] = 'redirect'
    if request.method == 'POST':
        # Set the destination to be used in the JS for the last action
        dst = request.POST['dst']
        data['dst'] = dst

        # Delete the table
        panda_db.delete_table(workflow.id)

        # Delete number of rows and columns
        workflow.nrows = 0
        workflow.ncols = 0
        workflow.n_filterd_rows = -1

        # Delete the column_names, column_types and column_unique
        workflow.column_names = ''
        workflow.column_types = ''
        workflow.column_unique = ''

        # Delete the info for QueryBuilder
        workflow.query_builder_ops = ''

        # Table name
        workflow.data_frame_table_name = ''

        # Save the workflow with the new fields.
        workflow.save()

        # Log the event
        ops.put(request.user,
                'workflow_data_flush',
                workflow,
                {'id': workflow.id,
                 'name': workflow.name})

        # Delete the conditions attached to all the actions attached to the
        # workflow.
        to_delete = Condition.objects.filter(
            action__workflow=workflow)
        for item in to_delete:
            ops.put(request.user,
                    workflow,
                    'condition_delete',
                    {'id': item.id,
                     'name': item.name})
        to_delete.delete()

        # In this case, the form is valid
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail', kwargs={'pk': pk})
    else:
        data['html_form'] = \
            render_to_string('workflow/includes/partial_workflow_flush.html',
                             {'workflow': workflow,
                              'dst': request.GET['dst']},
                             request=request)

    return JsonResponse(data)


@login_required
@user_passes_test(is_instructor)
def delete(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    data = dict()
    if request.method == 'POST':
        # Set the destination to be used in the JS for last action
        dst = request.POST['dst']
        data['dst'] = dst

        # Log the event
        ops.put(request.user,
                'workflow_delete',
                workflow,
                {'id': workflow.id,
                 'name': workflow.name})

        # Perform the delete operation
        workflow.delete()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True

        if dst == 'refresh':
            # Create the html_item_list to refresh
            workflows = Workflow.objects.filter(user=request.user)
            table = WorkflowTable(workflows)
            data['html_item_list'] = table.as_html(request)
        else:  # dst = redirect
            data['html_redirect'] = reverse('workflow:index')

    else:
        data['html_form'] = \
            render_to_string('workflow/includes/partial_workflow_delete.html',
                             {'workflow': workflow,
                              'dst': request.GET['dst']},
                             request=request)
    return JsonResponse(data)


@method_decorator(decorators, name='dispatch')
class WorkflowDetailView(generic.DetailView):
    model = Workflow
    template_name = 'workflow/detail.html'
    context_object_name = 'workflow'

    def get_object(self, queryset=None):
        obj = super(WorkflowDetailView, self).get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404()
        self.request.session['ontask_workflow_id'] = obj.id
        self.request.session['ontask_workflow_name'] = obj.name
        return obj

    def get_context_data(self, **kwargs):

        context = super(WorkflowDetailView, self).get_context_data(**kwargs)

        wflow_id = self.request.session['ontask_workflow_id']

        table_info = panda_db.workflow_table_info(wflow_id)

        if table_info is not None:
            context['table_info'] = table_info

        return context


@login_required
@user_passes_test(is_instructor)
def attributes(request):
    workflow = get_object_or_404(Workflow,
                                 pk=request.session['ontask_workflow_id'],
                                 user=request.user)
    attributes = {}
    if workflow.attributes != '':
        attributes = json.loads(workflow.attributes)

    # Get the form fields from the attributes and the current values
    form_fields = [(x, x + '__value', y)
                   for x, y in sorted(attributes.items())]

    # Create the form object with the form_fields just computed
    form = AttributeForm(request.POST or None, form_fields=form_fields)

    if request.method == 'POST':
        if form.is_valid():

            # Collect the data from the form and update the workflow
            new_attr = {}
            for key in sorted(attributes.keys()):
                new_attr[form.cleaned_data[key]] = \
                    form.cleaned_data[key + '__value']

            try:
                new_attr = json.dumps(new_attr)
            except Exception, e:
                messages.error(request, 'Unable to store attributes. '
                                        'Edit and retry.')
                return render(request,
                              'workflow/attributes.html',
                              {'form': form})

            # Log the event
            ops.put(request.user,
                    'workflow_attribute_update',
                    workflow,
                    {'id': workflow.id,
                     'name': workflow.name,
                     'attr': attributes})

            # update the db
            workflow.attributes = new_attr
            workflow.save()

            return redirect(reverse('workflow:detail',
                                    kwargs={'pk': workflow.id}))

    return render(request,
                  'workflow/attributes.html',
                  {'form': form})


# TODO: there is an issue with name spaces. In principle, there
# should be no duplicated names between attribute names, column
# names, and condition names. They can all appear in a template.

@login_required
@user_passes_test(is_instructor)
def attribute_create(request):
    # Get the workflow
    workflow = get_object_or_404(Workflow,
                                 pk=request.session['ontask_workflow_id'],
                                 user=request.user)
    data = dict()
    data['form_is_valid'] = False

    attributes = {}
    if workflow.attributes != '':
        attributes = json.loads(workflow.attributes)

    # Create the form object with the form_fields just computed
    form = AttributeItemForm(request.POST or None,
                             keys=attributes.keys())

    if request.method == 'POST':
        dst = request.POST['dst']
        if form.is_valid():
            attributes[form.cleaned_data['key']] = form.cleaned_data['value']
            workflow.attributes = json.dumps(attributes)
            workflow.save()

            # Log the event
            ops.put(request.user,
                    'workflow_attribute_create',
                    workflow,
                    {'id': workflow.id,
                     'name': workflow.name,
                     'attr_key': form.cleaned_data['key'],
                     'attr_val': form.cleaned_data['value']})

            data['form_is_valid'] = True
            data['dst'] = 'redirect'
            data['html_redirect'] = reverse('workflow:attributes')
    else:
        dst = request.GET['dst']

    context = {'form': form,
               'dst': dst}

    data['html_form'] = render_to_string(
        'workflow/includes/partial_attribute_create.html',
        context,
        request=request)

    return JsonResponse(data)


@login_required
@user_passes_test(is_instructor)
def attribute_delete(request):
    # Get the workflow
    workflow = get_object_or_404(Workflow,
                                 pk=request.session['ontask_workflow_id'],
                                 user=request.user)
    data = dict()
    data['form_is_valid'] = False
    key = request.GET.get('key', None)

    if request.method == 'POST' and key is not None:

        attributes = json.loads(workflow.attributes)
        val = attributes.pop(key, None)
        workflow.attributes = json.dumps(attributes)

        # Log the event
        ops.put(request.user,
                'workflow_attribute_delete',
                workflow,
                {'id': workflow.id,
                 'attr_key': key,
                 'attr_val': val})

        workflow.save()

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:attributes')
    else:
        key = request.GET['key']

    data['html_form'] = render_to_string(
        'workflow/includes/partial_attribute_delete.html',
        {'key': key},
        request=request)

    return JsonResponse(data)


# @login_required
# @user_passes_test(is_instructor)
def share(request, pk):
    return render(request, 'base.html')
