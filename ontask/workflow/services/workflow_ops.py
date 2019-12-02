# -*- coding: utf-8 -*-

"""Functions to manipulate other workflow ops."""
from typing import Dict

from django import http
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask import is_correct_email, models, tasks
from ontask.core import DataTablesServerSidePaging, OperationsColumn
from ontask.core.session_ops import store_workflow_in_session
from ontask.dataops.sql import get_rows, get_text_column_hash
from ontask.workflow.services import errors


class AttributeTable(tables.Table):
    """Table to render the list of attributes attached to a workflow."""

    name = tables.Column(verbose_name=_('Name'))

    value = tables.Column(verbose_name=_('Value'))  # noqa Z110

    operations = OperationsColumn(
        verbose_name='',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id']},
    )

    @staticmethod
    def render_name(record):
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

    class Meta:
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

    class Meta:
        """Fields, sequence and attributes."""

        fields = ('email', 'id')

        sequence = ('email', 'operations')

        attrs = {
            'class': 'table',
            'id': 'share-table',
            'th': {'class': 'dt-body-center'},
        }


def get_operations_context(workflow: models.Workflow) -> Dict:
    """Create the context to render the operations page.

    :param workflow: Workflow being manipulated.
    :return: Dictionary with the context.
    """
    return {
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


def check_luser_email_column_outdated(workflow: models.Workflow):
    """Detect if the luser_email column is up to date.

    :param workflow: Workflow being manipulated.
    :return: Side effect, md5_hash_is_outdated is updated.
    """
    if workflow.luser_email_column:
        md5_hash = get_text_column_hash(
            workflow.get_data_frame_table_name(),
            workflow.luser_email_column.name)
        if md5_hash != workflow.luser_email_column_md5:
            # Information is outdated
            workflow.lusers_is_outdated = True
            workflow.save()


def update_luser_email_column(
    user,
    pk: int,
    workflow: models.Workflow,
    column: models.Column,
):
    """Update the field luser_email in the workflow.

    :param user: User making the request
    :param pk: Column ID to obtain the user id
    :param workflow: Workflow being manipulated.
    :param column: Column being used to update the luser field.
    :return:
    """
    if not pk:
        # Empty pk, means reset the field.
        workflow.luser_email_column = None
        workflow.luser_email_column_md5 = ''
        workflow.lusers.set([])
        workflow.save()
        return

    table_name = workflow.get_data_frame_table_name()

    # Get the column content
    emails = get_rows(table_name, column_names=[column.name])

    # Verify that the column as a valid set of emails
    if not all(is_correct_email(row[column.name]) for row in emails):
        raise errors.OnTaskWorkflowIncorrectEmail(
            message=_('The selected column does not contain email addresses.'))

    # Update the column
    workflow.luser_email_column = column
    workflow.save()

    # Calculate the MD5 value
    md5_hash = get_text_column_hash(table_name, column.name)

    if workflow.luser_email_column_md5 == md5_hash:
        return

    # Change detected, run the update in batch mode
    workflow.luser_email_column_md5 = md5_hash

    # Log the event with the status "preparing updating"
    log_item = workflow.log(user, models.Log.WORKFLOW_UPDATE_LUSERS)

    # Push the update of lusers to batch processing
    tasks.execute_operation.delay(
        operation_type=models.Log.WORKFLOW_UPDATE_LUSERS,
        user_id=user.id,
        workflow_id=workflow.id,
        log_id=log_item.id)


def do_flush(request: http.HttpRequest, workflow: models.Workflow):
    """Perform the workflow data flush.

    :param request: Request received
    :param workflow: Workflow being manipulated.
    :return: Side effect, data is removed.
    """
    # Delete the table
    workflow.flush()
    workflow.refresh_from_db()
    # update the request object with the new number of rows
    store_workflow_in_session(request, workflow)
    workflow.log(request.user, models.Log.WORKFLOW_DATA_FLUSH)


def column_table_server_side(
    dt_page: DataTablesServerSidePaging,
    workflow: models.Workflow,
) -> Dict:
    """Create the server side object to render a page of the table of columns.

    :param dt_page: Table structure for paging a query set.
    :param workflow: Workflow being manipulated
    :return: Dictionary to return to the server to render the sub-page
    """
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

    return {
        'draw': dt_page.draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': final_qs,
    }
