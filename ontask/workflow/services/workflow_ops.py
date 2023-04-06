"""Functions to manipulate other workflow ops."""
from django import http
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from ontask import core, get_incorrect_email, models, tasks
from ontask.dataops import sql
from ontask.workflow import services


class AttributeTable(tables.Table):
    """Table to render the list of attributes attached to a workflow."""

    name = tables.Column(verbose_name=_('Name'))

    value = tables.Column(verbose_name=_('Value'))  # noqa Z110

    operations = core.OperationsColumn(
        verbose_name='',
        template_file='workflow/includes/partial_attribute_operations.html',
        template_context=lambda record: {'id': record['id']},
    )

    class Meta:
        """Select fields and attributes."""

        fields = ('operations', 'name', 'value')

        attrs = {'class': 'table', 'id': 'attribute-table'}


class WorkflowShareTable(tables.Table):
    """Class to render the table of shared users."""

    email = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=_('User'),
    )

    operations = core.OperationsColumn(
        orderable=False,
        template_file='workflow/includes/partial_share_operations.html',
        template_context=lambda elems: {'id': elems['id']},
        verbose_name=_('Operations'),
        attrs={'td': {'class': 'dt-body-center'}},
    )

    class Meta:
        """Fields, sequence and attributes."""

        fields = ('email', 'id')

        sequence = ('operations', 'email')

        attrs = {
            'class': 'table',
            'id': 'share-table',
            'th': {'class': 'dt-body-center'},
        }


def check_luser_email_column_outdated(workflow: models.Workflow):
    """Detect if the luser_email column is up to date.

    :param workflow: Workflow being manipulated.
    :return: Side effect, md5_hash_is_outdated is updated.
    """
    if workflow.luser_email_column:
        md5_hash = sql.get_text_column_hash(
            workflow.get_data_frame_table_name(),
            workflow.luser_email_column.name)
        if md5_hash != workflow.luser_email_column_md5:
            # Information is outdated
            workflow.lusers_is_outdated = True
            workflow.save(update_fields=['lusers_is_outdated'])


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
        workflow.save(update_fields=[
            'luser_email_column',
            'luser_email_column_md5'])
        return

    table_name = workflow.get_data_frame_table_name()

    # Get the column content
    emails = sql.get_rows(table_name, column_names=[column.name])

    # Verify that the column as a valid set of emails
    incorrect_email = get_incorrect_email([row[column.name] for row in emails])
    if incorrect_email:
        raise services.OnTaskWorkflowEmailError(
            message=_('Incorrect email addresses "{0}".').format(
                incorrect_email))

    # Update the column
    workflow.luser_email_column = column
    workflow.save(update_fields=['luser_email_column'])

    # Calculate the MD5 value
    md5_hash = sql.get_text_column_hash(table_name, column.name)

    if workflow.luser_email_column_md5 == md5_hash:
        return

    # Change detected, run the update in batch mode
    workflow.luser_email_column_md5 = md5_hash
    workflow.save(update_fields=['luser_email_column_md5'])

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
    core.store_workflow_in_session(request.session, workflow)
    workflow.log(request.user, models.Log.WORKFLOW_DATA_FLUSH)
