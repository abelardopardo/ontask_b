# -*- coding: utf-8 -*-

import gzip
from builtins import str
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _, ugettext
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

import dataops.sql_query
from action.models import Condition
from dataops import pandas_db, ops
from logs.models import Log
from workflow.serializers import (
    WorkflowExportSerializer,
    WorkflowImportSerializer
)


def store_workflow_nrows_in_session(request, obj):
    """
    Store the workflow id and name in the request.session dictionary
    :param request: Request object
    :param obj: Workflow object
    :return: Nothing. Store the id and the name in the session
    """

    request.session['ontask_workflow_rows'] = obj.nrows
    request.session.save()


def store_workflow_in_session(request, obj):
    """
    Store the workflow id, name, and number of rows in the
    request.session dictionary
    :param request: Request object
    :param obj: Workflow object
    :return: Nothing. Store the id, name and nrows in the session
    """

    request.session['ontask_workflow_id'] = obj.id
    request.session['ontask_workflow_name'] = obj.name
    store_workflow_nrows_in_session(request, obj)


def do_import_workflow_parse(user, name, file_item):
    """
    Three steps: read the GZIP file, create ther serializer, parse the data,
    check for validity and create the workflow
    :param user: User used for the operation
    :param name: Workflow name
    :param file_item: File item previously opened
    :return: workflow object or raise exception
    """

    data_in = gzip.GzipFile(fileobj=file_item)
    data = JSONParser().parse(data_in)

    # Serialize content
    workflow_data = WorkflowImportSerializer(
        data=data,
        context={'user': user, 'name': name}
    )

    # If anything went wrong, return the string to show to the form.
    if not workflow_data.is_valid():
        raise serializers.ValidationError(workflow_data.errors)

    # Save the new workflow
    workflow = workflow_data.save()

    try:
        pandas_db.check_wf_df(workflow)
    except AssertionError:
        # Something went wrong.
        if workflow:
            workflow.delete()
        raise

    return workflow


def do_import_workflow(user, name, file_item):
    """
    Receives a name and a file item (submitted through a form) and creates
    the structure of workflow, conditions, actions and data table.

    :param user: User record to use for the import (own all created items)
    :param name: Workflow name (it has been checked that it does not exist)
    :param file_item: File item obtained through a form
    :return:
    """

    try:
        workflow = do_import_workflow_parse(user, name, file_item)
    except IOError:
        return _('Incorrect file. Expecting a GZIP file (exported workflow).')
    except (TypeError, NotImplementedError) as e:
        return _('Unable to import workflow. Exception: {0}').format(e)
    except serializers.ValidationError as e:
        return _('Unable to import workflow. Validation error: {0}').format(e)
    except AssertionError as e:
        # Something went wrong.
        return _('Workflow data with incorrect structure.')
    except Exception as e:
        return _('Unable to import workflow: {0}').format(e)

    # Success
    # Log the event
    Log.objects.register(user,
                         Log.WORKFLOW_IMPORT,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name})
    return None


def do_export_workflow_parse(workflow, selected_actions=None):
    """
    Serialize the workflow and attach its content to a BytesIO object
    :param workflow: Workflow to serialize
    :param selected_actions: Subset of actions
    :return: BytesIO
    """
    # Get the info to send from the serializer
    serializer = WorkflowExportSerializer(
        workflow,
        context={'selected_actions': selected_actions}
    )
    to_send = JSONRenderer().render(serializer.data)

    # Get the in-memory file to compress
    zbuf = BytesIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(to_send)
    zfile.close()

    return zbuf


def do_export_workflow(workflow, selected_actions=None):
    """
    Proceed with the workflow export.
    :param workflow: Workflow record to export be included.
    :param selected_actions: A subset of actions to export
    :return: Page that shows a confirmation message and starts the download
    """
    # Get the in-memory compressed file
    zbuf = do_export_workflow_parse(workflow, selected_actions)

    suffix = datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = zbuf.getvalue()
    response = HttpResponse(compressed_content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = \
        'attachment; filename="ontask_workflow_{0}.gz"'.format(suffix)
    response['Content-Length'] = str(len(compressed_content))

    return response


def workflow_delete_column(workflow, column, cond_to_delete=None):
    """
    Given a workflow and a column, removes it from the workflow (and the
    corresponding data frame
    :param workflow: Workflow object
    :param column: Column object to delete
    :param cond_to_delete: List of conditions to delete after removing the
    column
    :return: Nothing. Effect reflected in the database
    """

    # Drop the column from the DB table storing the data frame
    dataops.sql_query.df_drop_column(workflow.get_data_frame_table_name(), column.name)

    # Reposition the columns above the one being deleted
    workflow.reposition_columns(column.position, workflow.ncols + 1)

    # Delete the column
    column.delete()

    # Update the information in the workflow
    workflow.ncols = workflow.ncols - 1
    workflow.save()

    if not cond_to_delete:
        # The conditions to delete are not given, so calculate them
        # Get the conditions/actions attached to this workflow
        cond_to_delete = [
            x for x in Condition.objects.filter(action__workflow=workflow)
            if column in x.columns.all()]

    # If a column disappears, the conditions that contain that variable
    # are removed
    actions_without_filters = []
    for condition in cond_to_delete:
        if condition.is_filter:
            actions_without_filters.append(condition.action)

        # Formula has the name of the deleted column. Delete it
        condition.delete()

    # Traverse the actions for which the filter has been deleted and reassess
    #  all their conditions
    # TODO: Expensive operation. See how to improve it.
    for action in actions_without_filters:
        action.update_n_rows_selected()

    # If a column disappears, the views that contain only that column need to
    # disappear as well as they are no longer relevant.
    for view in workflow.views.all():
        if view.columns.count() == 0:
            view.delete()

    return


def workflow_restrict_column(column):
    """
    Given a workflow and a column, modifies the column so that only the
    values already present are allowed for future updates.

    :param column: Column object to restrict
    :return: String with error or None if correct
    """

    # Load the data frame
    data_frame = pandas_db.load_table(
        column.workflow.get_data_frame_table_name())

    cat_values = set(data_frame[column.name].dropna())
    if not cat_values:
        # Column has no meaningful values. Nothing to do.
        return _('Column has no meaningful values')

    # Set categories
    column.set_categories(list(cat_values))
    column.save()

    # Re-evaluate the operands in the workflow
    column.workflow.set_query_builder_ops()
    column.workflow.save()

    # Correct execution
    return None


def clone_column(column, new_workflow=None, new_name=None):
    """
    Function that given a column clones it and changes workflow and name
    :param column: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """
    # Store the old object name before squashing it
    old_name = column.name
    old_position = column.position

    # Clone
    column.id = None

    # Update some of the fields
    if new_name:
        column.name = new_name
    if new_workflow:
        column.workflow = new_workflow

    # Set column at the end
    column.position = column.workflow.ncols + 1
    column.save()

    # Update the number of columns in the workflow
    column.workflow.ncols += 1
    column.workflow.save()

    # Reposition the columns above the one being deleted
    column.workflow.reposition_columns(column.position, old_position + 1)

    # Add the column to the table and update it.
    data_frame = pandas_db.load_table(
        column.workflow.get_data_frame_table_name())
    data_frame[new_name] = data_frame[old_name]
    ops.store_dataframe(data_frame, column.workflow)

    return column


def do_workflow_update_lusers(workflow, log_item):
    """
    Recalculate the elements in the field lusers of the workflow based on the
     fields luser_email_column and luser_email_column_MD5

    :param workflow: Workflow to update
    :param log_item: Log where to leave the status of the operation
    :return: Changes in the lusers ManyToMany relationships
    """

    # Get the column content
    emails = pandas_db.get_rows(
        workflow.get_data_frame_table_name(),
        [workflow.luser_email_column.name], None)

    result = []
    created = 0
    for __, uemail, in emails:
        luser = get_user_model().objects.filter(email=uemail).first()
        if not luser:
            # Create user
            if settings.DEBUG:
                # Define users with the same password in development
                password='boguspwd'
            else:
                password = get_random_string(length=50)
            luser = get_user_model().objects.create_user(
                email=uemail,
                password=password
            )
            created += 1

        result.append(luser)

    # Assign result
    workflow.lusers.set(result)

    # Report status
    log_item.payload['total_users'] = len(emails)
    log_item.payload['new_users'] = created
    log_item.payload['status'] = ugettext(
        'Learner emails successfully updated.'
    )
    log_item.save()

    return
