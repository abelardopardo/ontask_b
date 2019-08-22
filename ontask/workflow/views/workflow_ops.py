# -*- coding: utf-8 -*-

"""Views to flush, show details, column server side, etc."""

from typing import Optional

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import is_correct_email
from ontask.core import DataTablesServerSidePaging
from ontask.core.decorators import ajax_required, get_column, get_workflow
from ontask.core.permissions import is_instructor
from ontask.core.tables import OperationsColumn
from ontask.dataops.sql import get_rows, get_text_column_hash
from ontask.models import Column, Log, Workflow
from ontask.tasks import workflow_update_lusers
from ontask.workflow.access import store_workflow_in_session


class AttributeTable(tables.Table):
    """Table to render the list of attributes attached to a workflow."""

    name = tables.Column(verbose_name=_('Name'))

    value = tables.Column(verbose_name=_('Value'))

    operations = OperationsColumn(
        verbose_name='',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render name field as a link.

        Impossible to use LinkColumn because href="#". A template may be an
        overkill.
        """
        return format_html(
            '<a href="#" data-toggle="tooltip"'
            + ' class="js-attribute-edit" data-url="{0}" title="{1}">{2}</a>',
            reverse('workflow:attribute_edit', kwargs={'pk': record['id']}),
            _('Edit the attribute'),
            record['name'],
        )

    class Meta(object):
        """Select fields and attributes."""

        fields = ('name', 'value', 'operations')

        attrs = {'class': 'table', 'id': 'attribute-table'}


class WorkflowShareTable(tables.Table):
    """Class to render the table of shared users."""

    email = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=_('User'),
    )

    operations = OperationsColumn(
        orderable=False,
        template_file='workflow/includes/partial_share_operations.html',
        template_context=lambda elems: {'id': elems['id']},
        verbose_name='',
        attrs={'td': {'class': 'dt-body-center'}},
    )

    class Meta(object):
        """Fields, sequence and attributes."""

        fields = ('email', 'id')

        sequence = ('email', 'operations')

        attrs = {
            'class': 'table',
            'id': 'share-table',
            'th': {'class': 'dt-body-center'},
        }


@user_passes_test(is_instructor)
@get_workflow(s_related='luser_email_column', pf_related=['columns', 'shared'])
def operations(
    request: HttpRequest,
    workflow: Optional[Workflow],
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
        'attribute_table': AttributeTable([
            {'id': idx, 'name': key, 'value': kval}
            for idx, (key, kval) in enumerate(sorted(
                workflow.attributes.items()))],
            orderable=False,
        ),
        'share_table': WorkflowShareTable(
            workflow.shared.values('email', 'id').order_by('email'),
        ),
        'unique_columns': workflow.get_unique_columns(),
    }

    return render(request, 'workflow/operations.html', context)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def flush(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Render the view to flush a workflow."""
    if workflow.nrows == 0:
        # Table is empty, redirect to data upload
        return JsonResponse({'html_redirect': reverse('dataops:uploadmerge')})

    if request.method == 'POST':
        # Delete the table
        workflow.flush()
        workflow.refresh_from_db()
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
@ajax_required
@get_workflow()
def star(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Toggle the star mark in the workflow."""
    # Get the workflows with stars
    stars = request.user.workflows_star.all()
    if workflow in stars:
        workflow.star.remove(request.user)
        has_star = False
    else:
        workflow.star.add(request.user)
        has_star = True

    # Log the event
    Log.objects.register(
        request.user,
        Log.WORKFLOW_STAR,
        workflow,
        {'id': workflow.id, 'name': workflow.name, 'star': has_star})

    # In this case, the form is valid
    return JsonResponse({})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_workflow(pf_related='columns')
def column_ss(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Render the server side page for the table of columns.

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
        col_name = [
            'position',
            'name',
            'description_text',
            'data_type',
            'is_key'][dt_page.order_col]
        if dt_page.order_dir == 'desc':
            col_name = '-' + col_name
        qs = qs.order_by(col_name)

    if dt_page.search_value:
        qs = qs.filter(
            Q(name__icontains=dt_page.search_value)
            | Q(data_type__icontains=dt_page.search_value))
        records_filtered = qs.count()

    # Creating the result
    final_qs = []
    for col in qs[dt_page.start:dt_page.start + dt_page.length]:
        ops_string = render_to_string(
            'workflow/includes/workflow_column_operations.html',
            {'id': col.id, 'is_key': col.is_key},
        )

        final_qs.append({
            'number': col.position,
            'name': format_html(
                '<a href="#" class="js-workflow-column-edit"'
                + 'data-toggle="tooltip" data-url="{0}"'
                + 'title="{1}">{2}</a>',
                reverse('workflow:column_edit', kwargs={'pk': col.id}),
                _('Edit the parameters of this column'),
                col.name,
            ),
            'description': col.description_text,
            'type': col.get_simplified_data_type(),
            'key': '<span class="true">✔</span>' if col.is_key else '',
            'operations': ops_string,
        })

        if len(final_qs) == dt_page.length:
            break

    return JsonResponse({
        'draw': dt_page.draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': final_qs,
    })


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_column()
def assign_luser_column(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
    """Render the view to assign the luser column.

    AJAX view to assign the column with id PK to the field luser_email_column
    and calculate the hash

    :param request: HTTP request

    :param pk: Column id

    :return: JSON data
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _(
                'Workflow has no data. '
                + 'Go to "Manage table data" to upload data.'),
        )
        return JsonResponse({'html_redirect': reverse('action:index')})

    if not pk:
        # Empty pk, means reset the field.
        workflow.luser_email_column = None
        workflow.luser_email_column_md5 = ''
        workflow.lusers.set([])
        workflow.save()
        return JsonResponse({'html_redirect': ''})

    table_name = workflow.get_data_frame_table_name()

    # Get the column content
    emails = get_rows(table_name, column_names=[column.name])

    # Verify that the column as a valid set of emails
    if not all(is_correct_email(row[column.name]) for row in emails):
        messages.error(
            request,
            _('The selected column does not contain email addresses.'),
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
             'status': 'preparing updating'},
        )

        # Push the update of lusers to batch processing
        workflow_update_lusers.delay(
            request.user.id,
            workflow.id,
            log_item.id)

    workflow.lusers_is_outdated = False
    workflow.save()

    messages.success(
        request,
        _('The list of workflow users will be updated shortly.'),
    )
    return JsonResponse({'html_redirect': ''})
