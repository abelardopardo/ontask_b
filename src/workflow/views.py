# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from collections import OrderedDict

import django_tables2 as tables
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import action
import logs.ops
from action.models import Condition
from dataops import ops, pandas_db
from ontask.permissions import is_instructor, UserIsInstructor
from ontask.tables import OperationsColumn
from .forms import WorkflowForm
from .models import Workflow, Column
from .ops import (get_workflow,
                  unlock_workflow_by_id,
                  get_user_locked_workflow,
                  detach_dataframe)


class WorkflowTable(tables.Table):
    name = tables.Column(verbose_name=str('Name'))
    description_text = tables.Column(
        empty_values=[],
        verbose_name=str('Description')
    )
    nrows_cols = tables.Column(
        empty_values=[],
        verbose_name=str('Rows/Columns'),
        default='No data'
    )
    modified = tables.DateTimeColumn(verbose_name='Last modified')

    def __init__(self, data, *args, **kwargs):
        table_id = kwargs.pop('id')

        super(WorkflowTable, self).__init__(data, *args, **kwargs)
        # If an ID was given, pass it on to the table attrs.
        if table_id:
            self.attrs['id'] = table_id

    def render_name(self, record):
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('workflow:detail', kwargs={'pk': record['id']}),
                record['name']
            )
        )

    def render_nrows_cols(self, record):
        if record['nrows'] == 0 and record['ncols'] == 0:
            return "No data"

        return format_html("{0}/{1}".format(record['nrows'], record['ncols']))

    class Meta:
        model = Workflow

        fields = ('name', 'description_text', 'nrows_cols', 'modified')

        sequence = ('name', 'description_text', 'nrows_cols', 'modified')

        exclude = ('user', 'attributes', 'nrows', 'ncols', 'column_names',
                   'column_types', 'column_unique', 'query_builder_ops',
                   'data_frame_table_name')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'workflow-table'
        }


class WorkflowShareTable(tables.Table):
    email = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('User')
    )

    operations = OperationsColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='',
        orderable=False,
        template_file='workflow/includes/partial_share_operations.html',
        template_context=lambda x: {'id': x['id']}
    )

    class Meta:
        fields = ('email', 'id')

        sequence = ('email', 'operations')

        attrs = {
            'class': 'table display',
            'id': 'share-table',
            'th': {'class': 'dt-body-center'}
        }


def save_workflow_form(request, form, template_name):
    # Ajax response. Form is not valid until proven otherwise
    data = {'form_is_valid': False}

    if request.method == 'GET' or not form.is_valid():
        context = {'form': form}
        data['html_form'] = render_to_string(template_name,
                                             context,
                                             request=request)
        return JsonResponse(data)

    # Correct form submitted

    if not form.instance.id:
        # This is a new instance!
        form.instance.user = request.user
        form.instance.nrows = 0
        form.instance.ncols = 0
        form.instance.session_key = request.session.session_key
        log_type = 'workflow_create'
    else:
        log_type = 'workflow_update'

    # Save the instance
    try:
        workflow_item = form.save()
    except IntegrityError as e:
        form.add_error('name',
                       'A workflow with that name already exists')
        context = {'form': form}
        data['html_form'] = render_to_string(template_name,
                                             context,
                                             request=request)
        return JsonResponse(data)

    # Log event
    logs.ops.put(request.user,
                 log_type,
                 workflow_item,
                 {'id': workflow_item.id,
                  'name': workflow_item.name})

    # Here we can say that the form processing is done.
    data['form_is_valid'] = True
    data['html_redirect'] = reverse('workflow:index')

    return JsonResponse(data)


@user_passes_test(is_instructor)
def workflow_index(request):
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

    # Get the available workflows
    workflows = Workflow.objects.filter(
        Q(user=request.user) | Q(shared=request.user)
    ).distinct().values(
        'id',
        'name',
        'description_text',
        'nrows',
        'ncols',
        'modified'
    )

    # We include the table only if it is not empty.
    context = {}
    if workflows.count() > 0:
        context['table'] = WorkflowTable(workflows,
                                         id='workflow-table',
                                         orderable=False)

    return render(request, 'workflow/index.html', context)


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    form_class = WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_context_data(self, **kwargs):
        context = super(WorkflowCreateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        del args
        form = self.form_class()
        return save_workflow_form(request, form, self.template_name)

    def post(self, request, *args, **kwargs):
        del args
        form = self.form_class(request.POST)
        return save_workflow_form(request, form, self.template_name)


class WorkflowDetailView(UserIsInstructor, generic.DetailView):
    """
    @DynamicAttrs
    """
    model = Workflow
    template_name = 'workflow/detail.html'
    context_object_name = 'workflow'

    def get_object(self, queryset=None):
        old_obj = super(WorkflowDetailView, self).get_object(queryset=queryset)

        # Check if the workflow is locked
        obj = get_workflow(self.request, old_obj.id)
        if not obj:
            user = get_user_locked_workflow(old_obj)
            messages.error(
                self.request,
                'The workflow is being modified by user ' + user.email)
            return None

        # Remember the current workflow
        self.request.session['ontask_workflow_id'] = obj.id

        # Store the current workflow
        self.request.session['ontask_workflow_name'] = obj.name
        return obj

    def get_context_data(self, **kwargs):

        context = super(WorkflowDetailView, self).get_context_data(**kwargs)

        workflow_id = self.request.session.get('ontask_workflow_id', None)
        if not workflow_id:
            return context

        # Get the table information (if it exist)
        context['table_info'] = None
        if ops.workflow_id_has_table(self.object.id):
            context['table_info'] = {
                'num_rows': self.object.nrows,
                'num_cols': self.object.ncols,
                'num_actions': self.object.actions.all().count(),
                'num_attributes': len(self.object.attributes)}

        # put the number of key columns in the workflow
        context['num_key_columns'] = Column.objects.filter(
            workflow__id=workflow_id,
            is_key=True
        ).count()

        # Safety check for consistency (only in development)
        if settings.DEBUG:
            assert pandas_db.check_wf_df(self.object)

        return context


@user_passes_test(is_instructor)
def update(request, pk):
    """
    Update the workflow information (name, description)
    :param request: Request object
    :param pk: Workflow ID
    :return: JSON response
    """

    workflow = get_workflow(request, pk)
    if not workflow:
        return redirect('workflow:index')

    form = WorkflowForm(request.POST or None, instance=workflow)

    # If the user owns the workflow, proceed
    if workflow.user == request.user:
        return save_workflow_form(
            request,
            form,
            'workflow/includes/partial_workflow_update.html')

    # If the user does not own the workflow, notify error and go back to
    # index
    messages.error(request,
                   'You can only rename workflows you created.')
    if request.is_ajax():
        data = {'form_is_valid': True,
                'html_redirect': reverse('workflow:index')}
        return JsonResponse(data)

    return redirect('workflow:index')


@user_passes_test(is_instructor)
def flush(request, pk):
    workflow = get_workflow(request, pk)
    if not workflow:
        return redirect('workflow:index')

    data = dict()

    if request.user != workflow.user:
        # If the user does not own the workflow, notify error and go back to
        # index
        messages.error(
            request,
            'You can only flush the data of  workflows you created.')

        if request.is_ajax():
            data = {'form_is_valid': True,
                    'html_redirect': reverse('workflow:index')}
            return JsonResponse(data)

        return redirect('workflow:index')

    if request.method == 'POST':
        # Delete the table
        detach_dataframe(workflow)

        # Log the event
        logs.ops.put(request.user,
                     'workflow_data_flush',
                     workflow,
                     {'id': workflow.id,
                      'name': workflow.name})

        # Delete the conditions attached to all the actions attached to the
        # workflow.
        to_delete = Condition.objects.filter(
            action__workflow=workflow)
        for item in to_delete:
            logs.ops.put(request.user,
                         'condition_delete',
                         workflow,
                         {'id': item.id,
                          'name': item.name})
        to_delete.delete()

        # In this case, the form is valid
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail', kwargs={'pk': pk})
    else:
        data['html_form'] = \
            render_to_string('workflow/includes/partial_workflow_flush.html',
                             {'workflow': workflow},
                             request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def delete(request, pk):
    workflow = get_workflow(request, pk)
    if not workflow:
        return redirect('workflow:index')

    # Ajax result
    data = dict()

    # If the request is not done by the user, flat the error
    if workflow.user != request.user:
        messages.error(request,
                       'You can only delete workflows that you createds.')

        if request.is_ajax():
            data['form_is_valid'] = True
            data['html_redirect'] = reverse('workflow:index')
            return JsonResponse(data)

        return redirect('workflow:index')

    if request.method == 'POST':
        # Log the event
        logs.ops.put(request.user,
                     'workflow_delete',
                     workflow,
                     {'id': workflow.id,
                      'name': workflow.name})

        # Perform the delete operation
        workflow.delete()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
    else:
        data['html_form'] = \
            render_to_string('workflow/includes/partial_workflow_delete.html',
                             {'workflow': workflow},
                             request=request)
    return JsonResponse(data)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def column_ss(request, pk):
    """
    Given the workflow id and the request, return to DataTable the proper
    list of columns to be rendered.
    :param request: Http request received from DataTable
    :param pk: Workflow id
    :return: Data to visualize in the table
    """
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'error': 'Incorrect request. Unlable to process'})

    # If there is no DF, there are no columns to show, this should be
    # detected before this is executed
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': 'There is no data in the workflow'})

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        order_col = request.POST.get('order[0][column]', None)
        order_dir = request.POST.get('order[0][dir]', 'asc')
    except ValueError:
        return JsonResponse({'error': 'Incorrect request. Unable to process'})

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get the initial set
    qs = workflow.columns.all()
    recordsTotal = len(qs)
    recordsFiltered = recordsTotal

    # Reorder if required
    if order_col:
        col_name = ['name', 'data_type', 'is_key'][int(order_col)]
        if order_dir == 'desc':
            col_name = '-' + col_name
        qs = qs.order_by(col_name)

    if search_value:
        qs = qs.filter(Q(name__contains=search_value) |
                       Q(data_type__contains=search_value))
        recordsFiltered = len(qs)

    # Creating the result
    final_qs = []
    for col in qs[start:start + length]:
        ops_string = render_to_string(
            'workflow/includes/workflow_column_operations.html',
            {'id': col.id, 'is_key': col.is_key}
        )

        final_qs.append([
            col.name,
            col.data_type,
            '<span class="true">✔</span>' if col.is_key \
                  else '<span class="true">✘</span>',
            ops_string
        ])

        if len(final_qs) == length:
            break

    # Result to return as Ajax response
    data = {
        'draw': draw,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'data': final_qs
    }

    return JsonResponse(data)


@user_passes_test(is_instructor)
def clone(request, pk):
    """
    AJAX view to clone a workflow
    :param request: HTTP request
    :param pk: Workflow id
    :return: JSON data
    """

    # JSON response
    data = dict()

    # Get the current workflow
    workflow = get_workflow(request, pk)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Initial data in the context
    data['form_is_valid'] = False
    context = {'pk': pk,
               'name': workflow.name}

    if request.method == 'GET':
        data['html_form'] = render_to_string(
            'workflow/includes/partial_workflow_clone.html',
            context,
            request=request
        )
        return JsonResponse(data)

    # POST REQUEST

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + workflow.name
    while Workflow.objects.filter(name=new_name).exists():
        new_name = 'Copy of ' + new_name

    workflow.id = None
    workflow.name = new_name
    try:
        workflow.save()
    except IntegrityError:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:details',
                                        kwargs={'pk': workflow.id})
        messages.error(request, 'Unable to clone workflow')
        return JsonResponse(data)

    # Get the initial object back
    workflow_new = workflow
    workflow = get_workflow(request, pk)

    # Clone the data frame
    data_frame = pandas_db.load_from_db(workflow.pk)
    ops.store_dataframe_in_db(data_frame, workflow_new.id)

    # Clone actions
    action.ops.clone_actions([a for a in workflow.actions.all()], workflow_new)

    # Done!
    workflow_new.save()

    # Log event
    logs.ops.put(request.user,
                 'workflow_clone',
                 workflow_new,
                 {'id_old': workflow_new.id,
                  'id_new': workflow.id,
                  'name_old': workflow_new.name,
                  'name_new': workflow.name})

    messages.success(request,
                     'Workflow successfully cloned.')
    data['form_is_valid'] = True
    data['html_redirect'] = ""  # Reload page

    return JsonResponse(data)
