# -*- coding: utf-8 -*-


from builtins import range

import django_tables2 as tables
from celery.task.control import inspect
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
from django.utils.translation import ugettext_lazy as _

import action
from dataops import ops, pandas_db
from dataops.models import SQLConnection
from dataops.sqlcon_views import SQLConnectionTableAdmin
from logs.models import Log
from ontask.permissions import is_instructor, UserIsInstructor, is_admin
from ontask.tables import OperationsColumn
from .forms import WorkflowForm
from .models import Workflow, Column
from .ops import get_workflow


class AttributeTable(tables.Table):
    """
    Table to render the list of attributes attached to a workflow
    """
    name = tables.Column(verbose_name=_('Name'))
    value = tables.Column(verbose_name=_('Value'))
    operations = OperationsColumn(
        verbose_name='Operations',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id'], }
    )

    class Meta(object):
        fields = ('name', 'value', 'operations')
        attrs = {
            'class': 'table table-hover table-striped table-bordered',
            'style': 'min-width: 505px; width: 100%;',
            'id': 'attribute-table'
        }


class WorkflowShareTable(tables.Table):
    email = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=_('User')
    )

    operations = OperationsColumn(
        orderable=False,
        template_file='workflow/includes/partial_share_operations.html',
        template_context=lambda x: {'id': x['id']},
        verbose_name=_('Delete'),
        attrs={'td': {'class': 'dt-body-center'}},
    )

    class Meta(object):
        fields = ('email', 'id')

        sequence = ('email', 'operations')

        attrs = {
            'class': 'table table-hover table-striped table-bordered',
            'style': 'min-width: 505px; width: 100%;',
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
        log_type = Log.WORKFLOW_CREATE
        redirect = reverse('dataops:uploadmerge')
    else:
        log_type = Log.WORKFLOW_UPDATE
        redirect = ''

    # Save the instance
    try:
        workflow_item = form.save()
    except IntegrityError:
        form.add_error('name',
                       _('A workflow with that name already exists'))
        context = {'form': form}
        data['html_form'] = render_to_string(template_name,
                                             context,
                                             request=request)
        return JsonResponse(data)

    # Log event
    Log.objects.register(request.user,
                         log_type,
                         workflow_item,
                         {'id': workflow_item.id,
                          'name': workflow_item.name})

    # Set the new workflow as the current one
    workflow_item = get_workflow(request, workflow_item.id)
    if not workflow_item:
        messages.error(request,
                       _('The newly created workflow could not be accessed'))

    # Here we can say that the form processing is done.
    data['form_is_valid'] = True
    data['html_redirect'] = redirect

    return JsonResponse(data)


@user_passes_test(is_instructor)
def index(request):
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        Workflow.unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

    # Get the available workflows
    workflows = Workflow.objects.filter(
        Q(user=request.user) | Q(shared=request.user)
    ).distinct().order_by('name')

    # We include the table only if it is not empty.
    context = {
        'workflows': workflows,
        'nwflows': len(workflows)
    }

    # Report if Celery is not running properly
    if request.user.is_superuser:
        # Verify that celery is running!
        celery_stats = None
        try:
            celery_stats = inspect().stats()
        except Exception as e:
            pass
        if not celery_stats:
            messages.error(
                request,
                _('WARNING: Celery is not currently running. '
                  'Please configure it correctly.')
            )

    return render(request, 'workflow/index.html', context)


@user_passes_test(is_instructor)
def operations(request, pk):
    """
    Http request to serve the operations page for the workflow
    :param request: HTTP Request
    :param pk: primary key of the workflow
    :return:
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request, wid=pk)
    if not workflow:
        return redirect('workflow:index')

    # Context to render the page
    context = {
        'workflow': workflow,
        'attribute_table': AttributeTable(
            [{'id': idx, 'name': k, 'value': v}
             for idx, (k, v) in enumerate(sorted(workflow.attributes.items()))],
            orderable=False
        ),
        'share_table': WorkflowShareTable(
            workflow.shared.values('email', 'id').order_by('email')
        )
    }

    return render(request, 'workflow/operations.html', context)


@user_passes_test(is_admin)
def sql_connections(request):
    """
    Page to show and handle the SQL connections
    :param request: Request
    :return: Render the appropriate page.
    """
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        Workflow.unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

    context = {}

    conns = SQLConnection.objects.all().values(
        'id',
        'name',
        'description_txt',
        'conn_type',
        'conn_driver',
        'db_user',
        'db_password',
        'db_host',
        'db_port',
        'db_name',
        'db_table'
    )

    context['table'] = SQLConnectionTableAdmin(conns,
                                               id='sqlconn-table',
                                               orderable=False)

    return render(request, 'workflow/sql_connections.html', context)


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
        return obj

    def get_context_data(self, **kwargs):

        context = super(WorkflowDetailView, self).get_context_data(**kwargs)

        # Get the table information (if it exist)
        context['table_info'] = None
        if ops.workflow_id_has_table(self.object.id):
            context['table_info'] = {
                'num_rows': self.object.nrows,
                'num_cols': self.object.ncols,
                'num_actions': self.object.actions.all().count(),
                'num_attributes': len(self.object.attributes)}

        # put the number of key columns in the context
        context['num_key_columns'] = self.object.columns.filter(
            is_key=True
        ).count()

        # Guarantee that column position is set for backward compatibility
        columns = self.object.columns.all()
        if any(x.position == 0 for x in columns):
            # At least a column has index equal to zero, so reset all of them
            for idx, c in enumerate(columns):
                c.position = idx + 1
                c.save()

        # Safety check for consistency (only in development)
        if settings.DEBUG:
            pandas_db.check_wf_df(self.object)

            # Columns are properly numbered
            cpos = self.object.columns.all().values_list('position', flat=True)
            assert sorted(cpos) == list(range(1, len(cpos) + 1))

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
        # Workflow is not accessible. Go back to index page.
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('workflow:index')})

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
                   _('You can only rename workflows you created.'))
    data = {'form_is_valid': True,
            'html_redirect': ''}
    return JsonResponse(data)


@user_passes_test(is_instructor)
def flush(request, pk):
    workflow = get_workflow(request, pk)
    if not workflow:
        # Workflow is not accessible. Go back to index page.
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('workflow:index')})

    data = dict()

    if request.user != workflow.user:
        # If the user does not own the workflow, notify error and go back to
        # index
        messages.error(
            request,
            _('You can only flush the data of  workflows you created.'))

        if request.is_ajax():
            data = {'form_is_valid': True,
                    'html_redirect': reverse('workflow:index')}
            return JsonResponse(data)

        return redirect('workflow:index')

    if request.method == 'POST':
        # Delete the table
        workflow.flush()

        # Log the event
        Log.objects.register(request.user,
                             Log.WORKFLOW_DATA_FLUSH,
                             workflow,
                             {'id': workflow.id,
                              'name': workflow.name})

        # In this case, the form is valid
        data['form_is_valid'] = True
        data['html_redirect'] = ''
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
        # Workflow is not accessible. Go back to index page.
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('workflow:index')})

    # Ajax result
    data = dict()

    # If the request is not done by the user, flat the error
    if workflow.user != request.user:
        messages.error(request,
                       _('You can only delete workflows that you created.'))

        if request.is_ajax():
            data['form_is_valid'] = True
            data['html_redirect'] = reverse('workflow:index')
            return JsonResponse(data)

        return redirect('workflow:index')

    if request.method == 'POST':
        # Log the event
        Log.objects.register(request.user,
                             Log.WORKFLOW_DELETE,
                             workflow,
                             {'id': workflow.id,
                              'name': workflow.name})

        # And drop the table
        if pandas_db.is_wf_table_in_db(workflow):
            pandas_db.delete_table(pk)

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
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # If there is no DF, there are no columns to show, this should be
    # detected before this is executed
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': _('There is no data in the workflow')})

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        order_col = request.POST.get('order[0][column]', None)
        order_dir = request.POST.get('order[0][dir]', 'asc')
    except ValueError:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

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
        qs = qs.filter(Q(name__icontains=search_value) |
                       Q(data_type__icontains=search_value))
        recordsFiltered = len(qs)

    # Creating the result
    final_qs = []
    for col in qs[start:start + length]:
        ops_string = render_to_string(
            'workflow/includes/workflow_column_operations.html',
            {'id': col.id, 'is_key': col.is_key}
        )

        # The data type for integers or doubles is shown as 'number'
        col_data_type = col.data_type
        col_data_type_str = """<div data-toggle="tooltip" title="{0}">
                 <span class="fa fa-{1}"></span></div>"""
        if col_data_type == 'string':
            col_data_type_str = col_data_type_str.format('Text', 'italic')
        elif col_data_type == 'integer' or col_data_type == 'double':
            col_data_type_str = col_data_type_str.format('Number',
                                                         'percent')
        elif col_data_type == 'boolean':
            col_data_type_str = col_data_type_str.format('True/False',
                                                         'toggle-on')
        elif col_data_type == 'datetime':
            col_data_type_str = col_data_type_str.format('Date/Time',
                                                         'calendar-o')

        final_qs.append({
            'number': render_to_string(
                'workflow/includes/workflow_column_movement.html',
                {'column': col}
            ),
            'name': col.name,
            'description': col.description_text,
            'type': format_html(col_data_type_str),
            'key': '<span class="true">✔</span>' if col.is_key else '',
            'operations': ops_string
        })

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
        data['html_redirect'] = ''
        messages.error(request, _('Unable to clone workflow'))
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
    Log.objects.register(request.user,
                         Log.WORKFLOW_CLONE,
                         workflow_new,
                         {'id_old': workflow_new.id,
                          'id_new': workflow.id,
                          'name_old': workflow_new.name,
                          'name_new': workflow.name})

    messages.success(request,
                     _('Workflow successfully cloned.'))
    data['form_is_valid'] = True
    data['html_redirect'] = ""  # Reload page

    return JsonResponse(data)
