# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import generic
from django.conf import settings

import logs.ops
from action.models import Condition
from dataops import ops, pandas_db
from ontask.permissions import is_instructor, UserIsInstructor
from .forms import (WorkflowForm)
from .models import Workflow, Column
from .ops import (get_workflow,
                  unlock_workflow_by_id,
                  detach_dataframe)


class OperationsColumn(tables.Column):
    empty_values = []

    def __init__(self, *args, **kwargs):
        self.template_file = kwargs.pop('template_file')
        self.get_operation_id = kwargs.pop('get_operation_id')

        super(OperationsColumn, self).__init__(*args, **kwargs)
        self.attrs = {'td': {'class': 'dt-body-center'}}
        self.orderable = False

    def render(self, record, table):
        return render_to_string(self.template_file,
                                {'id': self.get_operation_id(record)})


class WorkflowTable(tables.Table):
    name = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Name')
    )

    description_text = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Description')
    )

    nrows_cols = tables.Column(
        empty_values=[],
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Rows/Columns'),
        default='No data'
    )

    modified = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Last modified'

    )

    operations = OperationsColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Operations',
        orderable=False,
        template_file='workflow/includes/partial_workflow_operations.html',
        get_operation_id=lambda x: x.id
    )

    def __init__(self, data, *args, **kwargs):
        table_id = kwargs.pop('id')

        super(WorkflowTable, self).__init__(data, *args, **kwargs)
        # If an ID was given, pass it on to the table attrs.
        if table_id:
            self.attrs['id'] = table_id

    def render_name(self, record):
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('workflow:detail', kwargs={'pk': record.id}),
                record.name
            )
        )

    def render_nrows_cols(self, record):
        if record.nrows == 0 and record.ncols == 0:
            return "No data"

        return format_html("{0}/{1}".format(record.nrows, record.ncols))

    class Meta:
        model = Workflow

        fields = ('name', 'description_text', 'nrows_cols', 'modified')

        sequence = ('name', 'description_text', 'nrows_cols', 'modified',
                    'operations')

        exclude = ('user', 'attributes', 'nrows', 'ncols', 'column_names',
                   'column_types', 'column_unique', 'query_builder_ops',
                   'data_frame_table_name')

        attrs = {
            'class': 'table display',
            'id': 'item-table'
        }


class WorkflowDetailTable(tables.Table):
    column_name = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Column')
    )

    column_type = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Type')
    )

    is_key = tables.BooleanColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Key?')
    )



    class Meta:
        attrs = {
            'class':
                'table table-striped table-bordered table-hover cell-border',
            'id': 'column-table',
            'th': {'class': 'dt-body-center'}
        }

        row_attrs = {
            'class': lambda record: 'success' if record['is_key'] else ''
        }

        empty_text = 'No data in the workflow. Go to the Dataops section to ' \
                     'upload some data.'


def save_workflow_form(request, form, template_name, is_new):
    # Ajax response
    data = dict()

    # The form is false (thus needs to be rendered again, until proven
    # otherwise
    data['form_is_valid'] = False

    if request.method == 'POST':
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
                workflow_item.session_key = request.session.session_key
                is_new = form.instance.pk is None
                # Save the workflow
                workflow_item.save()

                # Log event
                if is_new:
                    log_type = 'workflow_create'
                else:
                    log_type = 'workflow_update'

                logs.ops.put(request.user,
                             'workflow_update',
                             workflow_item,
                             {'id': workflow_item.id,
                              'name': workflow_item.name})

                # Ok, here we can say that the form is done.
                data['form_is_valid'] = True
                data['html_redirect'] = reverse('workflow:index')

    context = {'form': form}
    data['html_form'] = render_to_string(template_name,
                                         context,
                                         request=request)
    return JsonResponse(data)


@user_passes_test(is_instructor)
def workflow_index(request):
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

    # Get the available workflows
    workflows = Workflow.objects.filter(user=request.user)

    # We include the table only if it is not empty.
    context = {}
    if len(workflows) > 0:
        context['table'] = WorkflowTable(workflows,
                                         id='item-table',
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
        return save_workflow_form(request, form, self.template_name, True)

    def post(self, request, *args, **kwargs):
        del args
        form = self.form_class(request.POST)
        return save_workflow_form(request, form, self.template_name, True)


class WorkflowDetailView(UserIsInstructor, generic.DetailView):
    """
    @DynamicAttrs
    """
    model = Workflow
    template_name = 'workflow/detail.html'
    context_object_name = 'workflow'

    def get_object(self, queryset=None):
        obj = super(WorkflowDetailView, self).get_object(queryset=queryset)

        # Check if the workflow is locked
        obj = get_workflow(self.request, obj.id)
        if not obj:
            messages.error(
                self.request,
                'The workflow is being modified by another user.')
            return None

        # Remember the current workflow
        self.request.session['ontask_workflow_id'] = obj.id
        # Store the current session to lock the workflow
        obj.session_key = self.request.session.session_key
        obj.save()
        self.request.session['ontask_workflow_name'] = obj.name
        return obj

    def get_context_data(self, **kwargs):

        context = super(WorkflowDetailView, self).get_context_data(**kwargs)

        wflow_id = self.request.session.get('ontask_workflow_id', None)
        if not wflow_id:
            return context

        # Get the table information (if it exist)
        table_info = ops.workflow_table_info(self.object)
        if table_info is not None:
            table = WorkflowDetailTable(
                table_info['table'],
                orderable=False)
            table_info['table_data'] = table
            context['table_info'] = table_info

        # put the number of key columns in the workflow
        context['num_key_columns'] = Column.objects.filter(
            workflow__id=wflow_id,
            is_key=True
        ).count()

        # Safety check for consistency (only in development)
        if settings.DEBUG:
            assert pandas_db.check_wf_df(self.object)

        return context


@user_passes_test(is_instructor)
def update(request, pk):
    workflow = get_workflow(request, pk)
    if not workflow:
        return redirect('workflow:index')

    form = WorkflowForm(request.POST or None, instance=workflow)

    # If the user owns the workflow, proceed
    if workflow.user == request.user:
        return save_workflow_form(
            request,
            form,
            'workflow/includes/partial_workflow_update.html',
            False)

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
