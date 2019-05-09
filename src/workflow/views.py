# -*- coding: utf-8 -*-


from builtins import range
from typing import Optional

import django_tables2 as tables
from celery.task.control import inspect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.datatables import DataTablesServerSidePaging
from dataops.pandas import check_wf_df, load_table, store_dataframe
from dataops.sql.column_queries import get_text_column_hash
from dataops.sql.row_queries import get_rows
from logs.models import Log
from ontask import is_correct_email, create_new_name
from ontask.decorators import access_workflow, get_workflow
from ontask.permissions import is_instructor, UserIsInstructor
from ontask.tables import OperationsColumn
from ontask.tasks import workflow_update_lusers
from .forms import WorkflowForm
from .models import Workflow
from .ops import store_workflow_in_session


class AttributeTable(tables.Table):
    """
    Table to render the list of attributes attached to a workflow
    """
    name = tables.Column(verbose_name=_('Name'))
    value = tables.Column(verbose_name=_('Value'))
    operations = OperationsColumn(
        verbose_name='',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id'], }
    )

    def render_name(self, record):
        return format_html(
            """<a href="#" data-toggle="tooltip" 
                  class="js-attribute-edit" data-url="{0}"
                  title="{1}">{2}</a>""",
            reverse('workflow:attribute_edit', kwargs={'pk': record['id']}),
            _('Edit the attribute'),
            record['name']
        )

    class Meta(object):
        fields = ('name', 'value', 'operations')
        attrs = {
            'class': 'table',
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
        verbose_name='',
        attrs={'td': {'class': 'dt-body-center'}},
    )

    class Meta(object):
        fields = ('email', 'id')

        sequence = ('email', 'operations')

        attrs = {
            'class': 'table',
            'id': 'share-table',
            'th': {'class': 'dt-body-center'}
        }


def save_workflow_form(
    request: HttpRequest,
    form,
    template_name: str
) -> JsonResponse:
    """Save the workflow to create a form.

    :param request:

    :param form:

    :param template_name:

    :return:
    """
    if request.method == 'POST' and form.is_valid():
        if not form.instance.id:
            # This is a new instance!
            form.instance.user = request.user
            form.instance.nrows = 0
            form.instance.ncols = 0
            log_type = Log.WORKFLOW_CREATE
            redirect_url = reverse('dataops:uploadmerge')
        else:
            log_type = Log.WORKFLOW_UPDATE
            redirect_url = ''

        # Save the instance
        try:
            workflow_item = form.save()
        except IntegrityError:
            form.add_error(
                'name',
                _('A workflow with that name already exists'))
            context = {'form': form}
            return JsonResponse({
                'html_form': render_to_string(
                    template_name,
                    {'form': form},
                    request=request),
            })

        # Log event
        Log.objects.register(
            request.user,
            log_type,
            workflow_item,
            {
                'id': workflow_item.id,
                'name': workflow_item.name,
            },
        )

        # Here we can say that the form processing is done.
        return JsonResponse({'html_redirect': redirect_url})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form},
            request=request),
    })

@user_passes_test(is_instructor)
def index(request):
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        Workflow.unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

    workflows = request.user.workflows_owner.all() \
                | request.user.workflows_shared.all()
    workflows = workflows.distinct()

    # We include the table only if it is not empty.
    context = {
        'workflows': workflows.order_by('name'),
        'nwflows': len(workflows)
    }

    # Report if Celery is not running properly
    if request.user.is_superuser:
        # Verify that celery is running!
        celery_stats = None
        try:
            celery_stats = inspect().stats()
        except Exception:
            pass
        if not celery_stats:
            messages.error(
                request,
                _('WARNING: Celery is not currently running. '
                  'Please configure it correctly.')
            )

    return render(request, 'workflow/index.html', context)


@user_passes_test(is_instructor)
@get_workflow(s_related='luser_email_column', pf_related=['columns', 'shared'])
def operations(
    request: HttpRequest,
    workflow: Optional[Workflow]
) -> HttpResponse:
    """Http request to serve the operations page for the workflow.

    :param request: HTTP Request

    :return:
    """
    # Check if lusers is active and if so, if it needs to be refreshed
    if workflow.luser_email_column:
        md5_hash = get_text_column_hash(
            workflow.get_data_frame_table_name(),
            workflow.luser_email_column.name)
        if md5_hash != workflow.luser_email_column_md5:
            # Information is outdated
            workflow.lusers_is_outdated = True
            workflow.save()

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
        ),
        'unique_columns': workflow.get_unique_columns()
    }

    return render(request, 'workflow/operations.html', context)


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    form_class = WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> JsonResponse:
        del args
        return save_workflow_form(
            request,
            self.form_class(),
            self.template_name)

    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        del args
        del kwargs
        return save_workflow_form(
            request,
            self.form_class(request.POST),
            self.template_name)


class WorkflowDetailView(UserIsInstructor, generic.DetailView):
    """
    @DynamicAttrs
    """
    model = Workflow
    template_name = 'workflow/detail.html'
    context_object_name = 'workflow'

    def get_object(self, queryset=None):
        old_obj = super().get_object(queryset=queryset)

        # Check if the workflow is locked
        obj = access_workflow(self.request,
                              old_obj.id,
                              prefetch_related=['actions', 'columns'])
        return obj

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # Get the table information (if it exist)
        context['table_info'] = None
        if self.object.has_table():
            context['table_info'] = {
                'num_rows': self.object.nrows,
                'num_cols': self.object.ncols,
                'num_actions': self.object.actions.count(),
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
            check_wf_df(self.object)

            # Columns are properly numbered
            cpos = self.object.columns.all().values_list('position', flat=True)
            assert sorted(cpos) == list(range(1, len(cpos) + 1))

        return context


@user_passes_test(is_instructor)
@get_workflow()
def update(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Update the workflow information (name, description).

    :param request: Request object

    :param pk: Workflow ID

    :return: JSON response
    """
    form = WorkflowForm(request.POST or None, instance=workflow)

    # If the user owns the workflow, proceed
    if workflow.user == request.user:
        return save_workflow_form(
            request,
            form,
            'workflow/includes/partial_workflow_update.html')

    # If the user does not own the workflow, notify error and go back to
    # index
    messages.error(
        request,
        _('You can only rename workflows you created.'))
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@get_workflow()
def flush(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    if workflow.nrows == 0:
        # Table is empty, redirect to data upload
        return JsonResponse({'html_redirect': reverse('dataops:uploadmerge')})

    if request.user != workflow.user:
        # If the user does not own the workflow, notify error and go back to
        # index
        messages.error(
            request,
            _('You can only flush the data of  workflows you created.'))

        if request.is_ajax():
            return JsonResponse({'html_redirect': reverse('home')})

        return redirect('home')

    if request.method == 'POST':
        # Delete the table
        workflow.flush()

        # update the request object with the new number of rows
        store_workflow_in_session(request, workflow)

        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_DATA_FLUSH,
            workflow,
            {'id': workflow.id, 'name': workflow.name})

        # In this case, the form is valid
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_flush.html',
            {'workflow': workflow},
            request=request),
    })


@user_passes_test(is_instructor)
@get_workflow()
def delete(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Delete a workflow."""
    # If the request is not done by the user, flat the error
    if workflow.user != request.user:
        messages.error(request,
                       _('You can only delete workflows that you created.'))

        if request.is_ajax():
            return JsonResponse({'html_redirect': reverse('home')})

        return redirect('home')

    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_DELETE,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name})

        # Perform the delete operation
        workflow.delete()

        # In this case, the form is valid anyway
        return JsonResponse({'html_redirect': reverse('home')})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_delete.html',
            {'workflow': workflow},
            request=request)
    })


@user_passes_test(is_instructor)
@get_workflow()
def clone(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Clone a workflow.

    :param request: HTTP request

    :param pk: Workflow id

    :return: JSON data
    """
    # Get the current workflow
    # Initial data in the context
    context = {'pk': wid, 'name': workflow.name}

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_workflow_clone.html',
                context,
                request=request),
        })

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + workflow.name
    while Workflow.objects.filter(name=new_name).exists():
        new_name = 'Copy of ' + new_name

    workflow.id = None
    workflow.name = create_new_name(
        workflow.name,
        Workflow.objects.filter(
            Q(workflow__user=request.user) | Q(workflow__shared=request.user)
        )
    )

    try:
        workflow.save()
    except IntegrityError:
        messages.error(request, _('Unable to clone workflow'))
        return JsonResponse({'html_redirect': ''})

    # Get the initial object back
    workflow_new = workflow
    workflow = access_workflow(request, wid, prefetch_related='actions')

    # Clone the data frame
    data_frame = load_table(workflow.get_data_frame_table_name())
    store_dataframe(data_frame, workflow_new)

    # Clone actions
    for action in workflow.actions.all():
        action.ops.clone_action(action, workflow_new)

    # Done!
    workflow_new.save()

    # Log event
    Log.objects.register(
        request.user,
        Log.WORKFLOW_CLONE,
        workflow_new,
        {
            'id_old': workflow_new.id,
            'id_new': workflow.id,
            'name_old': workflow_new.name,
            'name_new': workflow.name})

    messages.success(
        request,
        _('Workflow successfully cloned.'))
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
@get_workflow(pf_related='columns')
def column_ss(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """
    Given the workflow id and the request, return to DataTable the proper
    list of columns to be rendered.
    :param request: Http request received from DataTable
    :return: Data to visualize in the table
    """
    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get the initial set
    qs = workflow.columns.all()
    records_total = qs.count()
    records_filtered = records_total

    # Reorder if required
    if dt_page.order_col:
        col_name = ['position',
                    'name',
                    'description_text',
                    'data_type',
                    'is_key'][dt_page.order_col]
        if dt_page.order_dir == 'desc':
            col_name = '-' + col_name
        qs = qs.order_by(col_name)

    if dt_page.search_value:
        qs = qs.filter(Q(name__icontains=dt_page.search_value) |
                       Q(data_type__icontains=dt_page.search_value))
        records_filtered = qs.count()

    # Creating the result
    final_qs = []
    for col in qs[dt_page.start:dt_page.start + dt_page.length]:
        ops_string = render_to_string(
            'workflow/includes/workflow_column_operations.html',
            {'id': col.id, 'is_key': col.is_key}
        )

        final_qs.append({
            'number': col.position,
            'name': format_html(
                """<a href="#" class="js-workflow-column-edit"
                  data-toggle="tooltip" data-url="{0}"
                  title="{1}">{2}</a>""",
                reverse('workflow:column_edit', kwargs={'pk': col.id}),
                _('Edit the parameters of this column'),
                col.name
            ),
            'description': col.description_text,
            'type': col.get_simplified_data_type(),
            'key': '<span class="true">✔</span>' if col.is_key else '',
            'operations': ops_string
        })

        if len(final_qs) == dt_page.length:
            break

    # Result to return as Ajax response
    data = {
        'draw': dt_page.draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': final_qs
    }

    return JsonResponse(data)


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'lusers'])
def assign_luser_column(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """
    AJAX view to assign the column with id PK to the field luser_email_column
    and calculate the hash

    :param request: HTTP request
    :param wid: Column id
    :return: JSON data
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              'Go to "Manage table data" to upload data.')
        )
        return JsonResponse({'html_redirect': reverse('action:index')})

    if not wid:
        # Empty pk, means reset the field.
        workflow.luser_email_column = None
        workflow.luser_email_column_md5 = ''
        workflow.lusers.set([])
        workflow.save()
        return JsonResponse({'html_redirect': ''})

    # Get the column
    column = workflow.columns.filter(pk=wid).first()

    if not column:
        messages.error(
            request,
            _('Incorrect column selected. Please select a key column.')
        )
        return JsonResponse({'html_redirect': ''})

    table_name = workflow.get_data_frame_table_name()

    # Get the column content
    emails = get_rows(table_name, [column.name], None)

    # Verify that the column as a valid set of emails
    if not all([is_correct_email(email_val) for __, email_val in emails]):
        messages.error(
            request,
            _('The selected column does not contain email addresses.')
        )
        return JsonResponse({'html_redirect': ''})

    # Update the column
    workflow.luser_email_column = column
    workflow.save()

    # Calculate the MD5 value
    md5_hash = get_text_column_hash(table_name, column.name)

    if workflow.luser_email_column_md5 != md5_hash:
        # Change detected, run the update in batch mode
        workflow.luser_email_column_md5 = md5_hash

        # Log the event with the status "preparing updating"
        log_item = Log.objects.register(
            request.user,
            Log.WORKFLOW_UPDATE_LUSERS,
            workflow,
            {'id': workflow.id,
             'column': column.name,
             'status': 'preparing updating'}
        )

        # Push the update of lusers to batch processing
        workflow_update_lusers.delay(request.user.id,
                                     workflow.id,
                                     log_item.id)

    workflow.lusers_is_outdated = False
    workflow.save()

    messages.success(
        request,
        _('The list of workflow users will be updated shortly.')
    )
    return JsonResponse({'html_redirect': ''})
