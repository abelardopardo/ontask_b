# -*- coding: utf-8 -*-


import gzip
from builtins import str
from datetime import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from action.models import Condition
from dataops import pandas_db, ops
from logs.models import Log
from workflow.serializers import (
    WorkflowExportSerializer,
    WorkflowImportSerializer
)
from .models import Workflow


def store_workflow_in_session(request, obj):
    """
    Store the workflow id and name in the request.session dictionary
    :param request: Request object
    :param obj: Workflow object
    :return: Nothing. Store the id and the name in the session
    """

    request.session['ontask_workflow_id'] = obj.id
    request.session['ontask_workflow_name'] = obj.name
    request.session.save()


def get_workflow(request, wid=None, select_related=None, prefetch_related=None):
    """
    Function that gets the workflow that the user (in the current request) is
    using.
    :param request: HTTP request object
    :param wid: Workflow id to get. If not given, taken from the request
    session
    :param select_related: Field to add as select_related query filter
    :param prefetch_related: Field to add as prefetch_related query filter
    :return: Workflow object or None (if error)
    """

    # Obtain the workflow id stored in the session
    sid = request.session.get('ontask_workflow_id')

    if (not wid) and (not sid):
        # No key was given and none was found in the session (anomaly)
        return None

    update_session = False

    if wid is None:
        # No WID provided, but the session contains one, carry on with this one
        wid = sid
    elif sid is None:
        # Update the value in the session
        update_session = True
    elif sid != wid:
        Workflow.unlock_workflow_by_id(sid)
        # Update the value in the session
        update_session = True

    # Lock the workflow object while deciding if it is accessible or not to
    # avoid race conditions.
    with cache.lock('ONTASK_WORKFLOW_{0}'.format(wid)):

        # Step 1: Get the workflow that is being accessed
        try:
            # Query to get the workflow
            workflow = Workflow.objects.filter(
                id=wid).filter(
                Q(user=request.user) | Q(shared__id=request.user.id)
            ).first()

            if not workflow:
                # The object was not found.
                messages.error(request, _('Incorrect workflow request'))
                return None

            # Apply select if given
            if select_related:
                workflow = workflow.select_related(select_related)

            # Apply prefetch if given
            if prefetch_related:
                workflow = workflow.prefetch_related(prefetch_related)

            # Step 2: If the workflow is locked by this user session, return
            # correct result (the session_key may be None if using the API)
            if request.session.session_key == workflow.session_key:
                return workflow

            # Step 3: If the workflow is unlocked, LOCK and return
            if not workflow.session_key:
                # Workflow is unlocked. Proceed to lock
                workflow.lock(request, True)
                if update_session:
                    # If the session does not have this info, update.
                    store_workflow_in_session(request, workflow)
                return workflow

            # Step 4: The workflow is locked. See if the session locking it is
            # still valid
            try:
                session = Session.objects.get(session_key=workflow.session_key)
            except Session.DoesNotExist:
                # An exception means that the session stored as locking the
                # workflow is no longer in the session table, so the user can
                # access the workflow
                workflow.lock(request, True)
                if update_session:
                    # If the session does not have this info, update.
                    store_workflow_in_session(request, workflow)
                return workflow

            # Get the owner of the session locking the workflow
            owner = get_user_model().objects.get(
                id=session.get_decoded().get('_auth_user_id')
            )

            # Step 5: The workflow is locked by a session that is valid. See
            # if the session locking happens to be from the same user (a
            # previous session that has not been properly closed, or an API
            # call from the same user  )
            if owner == request.user:
                workflow.lock(request)
                if update_session:
                    # If the session does not have this info, update.
                    store_workflow_in_session(request, workflow)
                return workflow

            # Step 6: The workflow is locked by an existing session. See if the
            # session is valid
            if session.expire_date >= timezone.now():
                messages.error(
                    request,
                    _('The workflow is being modified by user {0}').format(
                        owner.email
                    )
                )
                # The session currently locking the workflow has an expire
                # date in the future from now. So, no access is granted.
                return None

            # The workflow is locked by a session that has expired. Take the
            # workflow and lock it with the current session.
            workflow.lock(request)
            if update_session:
                # If the session does not have this info, update.
                store_workflow_in_session(request, workflow)
        except Exception:
            # Something went wrong when fetching the object
            messages.error(request,
                           _('The workflow could not be accessed'))
            return None

        # All good. Return workflow.
        return workflow


def detach_dataframe(workflow):
    """
    Given a workflow object, delete its dataframe
    :param workflow:
    :return: Nothing, the workflow object is updated
    """
    pandas_db.delete_table(workflow.get_data_frame_table_name())

    # Delete number of rows and columns
    workflow.nrows = 0
    workflow.ncols = 0
    workflow.n_filterd_rows = -1
    workflow.save()

    # Delete the column_names, column_types and column_unique
    workflow.columns.delete()

    # Delete the info for QueryBuilder
    workflow.set_query_builder_ops()

    # Table name
    workflow.data_frame_table_name = ''

    # Save the workflow with the new fields.
    workflow.save()


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
    workflow = workflow_data.save(user=user, name=name)

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
        return _('Unable to import workflow (Exception: {0})').format(e)
    except serializers.ValidationError as e:
        return _('Unable to import workflow. Validation error ({0})').format(e)
    except AssertionError:
        # Something went wrong.
        return _('Workflow data with incorrect structure.')
    except Exception as e:
        return _('Unable to import workflow (Exception: {0})').format(e)

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
    pandas_db.df_drop_column(workflow.get_data_frame_table_name(), column.name)

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
    data_frame = pandas_db.load_from_db(
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
    data_frame = pandas_db.load_from_db(
        column.workflow.get_data_frame_table_name())
    data_frame[new_name] = data_frame[old_name]
    ops.store_dataframe(data_frame, column.workflow)

    return column


def reposition_column_and_update_df(workflow, column, to_idx):
    """

    :param workflow: Workflow object for which the repositioning is done
    :param column: column object to relocate
    :param to_idx: Destination index of the given column
    :return: Content reflected in the DB
    """

    # df = pandas_db.load_from_db(workflow.get_data_frame_table_name())
    workflow.reposition_columns(column.position, to_idx)
    column.position = to_idx
    column.save()
