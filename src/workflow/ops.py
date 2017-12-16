# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import gzip

import cStringIO
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from action.models import Condition
from dataops import formula_evaluation, pandas_db, ops
from .models import Workflow, Column
from .serializers import (WorkflowExportSerializer, WorkflowImportSerializer)
from rest_framework import serializers


def lock_workflow(request, workflow):
    """
    Function that sets the session key in the workflow to flag that is locked.
    :param request: HTTP request
    :param workflow: workflow to lock
    :return:
    """
    workflow.session_key = request.session.session_key
    workflow.save()


def unlock_workflow_by_id(wid):
    """
    Removes the session_key from the workflow with given id
    :param wid: Workflow id
    :return:
    """
    try:
        workflow = Workflow.objects.get(id=wid)
    except ObjectDoesNotExist:
        return

    # Workflow exists, unlock
    unlock_workflow(workflow)


def unlock_workflow(workflow):
    """
    Removes the session_key from the workflow
    :param workflow:
    :return:
    """
    workflow.session_key = ''
    workflow.save()


def is_locked(workflow):
    """
    :param workflow: workflow object to check if it is locked
    :return: Is the given workflow locked?
    """

    if not workflow.session_key:
        # No key in the workflow, then it is not locked.
        return False

    try:
        session = Session.objects.get(session_key=workflow.session_key)
    except ObjectDoesNotExist:
        # Session does not exist, then it is not locked
        return False

    # Session is in the workflow and in the session table. Locked if expire
    # date is less that current time.
    return session.expire_date < timezone.now()


def get_workflow(request, wid=None):
    """
    Function that gets the workflow that the user (in the current request) is
    using.
    :param request: HTTP request object
    :param wid: Workflow id to get. If not given, taken from the request
    session
    :return: Workflow object or None (if error)
    """

    # Step 1: Get the workflow that is being accessed
    try:
        # If there is no wid given, take it from the session. Search for
        # workflow that is either owned by the user or shared with her.
        if not wid:
            wid = request.session['ontask_workflow_id']

        workflow = Workflow.objects.filter(
            Q(user=request.user) | Q(shared__id=request.user.id)
        ).distinct().get(id=wid)
    except (KeyError, ObjectDoesNotExist):
        # No workflow or value set in the session, flag error.
        return None

    # Step 2: If the workflow is locked by this user session, return correct
    # result
    if request.session.session_key == workflow.session_key:
        return workflow

    # Step 3: If the workflow is unlocked, lock and return
    if not workflow.session_key:
        # Workflow is unlocked. Proceed to lock
        lock_workflow(request, workflow)
        return workflow

    # Step 4: The workflow is locked. See if the session locking it is
    # still valid
    try:
        session = Session.objects.get(session_key=workflow.session_key)
    except Session.DoesNotExist:
        # An exception means that the session stored as locking the
        # workflow is no longer in the session table, so the user can access
        # the workflow
        lock_workflow(request, workflow)
        return workflow

    # Get the owner of the session locking the workflow
    owner = get_user_model().objects.get(
        id=session.get_decoded().get('_auth_user_id')
    )

    # Step 5: The workflow is locked by a session that is valid. See if the
    # session locking it happens to be from the same user (a previous session
    # that has not been properly closed)
    if owner == request.user:
        lock_workflow(request, workflow)
        return workflow

    # Step 6: The workflow is locked by an existing session. See if the
    # session is valid
    if session.expire_date >= timezone.now():
        # The session currently locking the workflow
        # has an expire date in the future from now. So, no access is granted.
        return None

    # The workflow is locked by a session that has expired. Take the workflow
    # and lock it with the current session.
    lock_workflow(request, workflow)
    return workflow


def get_user_locked_workflow(workflow):
    """
    Given a workflow that is supposed to be locked, it returns the user that
    is locking it.
    :param workflow:
    :return:
    """
    session = Session.objects.get(session_key=workflow.session_key)
    session_data = session.get_decoded()
    return get_user_model().objects.get(id=session_data.get('_auth_user_id'))


def detach_dataframe(workflow):
    """
    Given a workflow object, delete its dataframe
    :param workflow:
    :return: Nothing, the workflow object is updated
    """
    pandas_db.delete_table(workflow.id)

    # Delete number of rows and columns
    workflow.nrows = 0
    workflow.ncols = 0
    workflow.n_filterd_rows = -1
    workflow.save()

    # Delete the column_names, column_types and column_unique
    Column.objects.filter(workflow__id=workflow.id).delete()

    # Delete the info for QueryBuilder
    workflow.set_query_builder_ops()

    # Table name
    workflow.data_frame_table_name = ''

    # Save the workflow with the new fields.
    workflow.save()


def do_import_workflow(user, name, file_item):
    """
    Receives a name and a file item (submitted through a form) and creates
    the structure of workflow, conditions, actions and data table.

    :param user: User record to use for the import (own all created items)
    :param name: Workflow name (it has been checked that it does not exist)
    :param file_item: File item obtained through a form
    :return:
    """

    data_in = gzip.GzipFile(fileobj=file_item)
    data = JSONParser().parse(data_in)
    # Serialize content
    workflow_data = WorkflowImportSerializer(
        data=data,
        context={'user': user, 'name': name}
    )

    # If anything went wrong, return the string to show to the form.
    workflow = None
    try:
        if not workflow_data.is_valid():
            return 'Unable to import the workflow' + ' (' + \
                   workflow_data.errors + ')'

        # Save the new workflow
        workflow = workflow_data.save(user=user, name=name)
    except (TypeError, NotImplementedError) as e:
        return 'Unable to import workflow (Exception: ' + e.message + ')'
    except serializers.ValidationError as e:
        return 'Unable to import workflow due to a validation error'

    if not pandas_db.check_wf_df(workflow):
        # Something went wrong.
        workflow.delete()
        return 'Workflow data with incorrect structure.'

    # Success
    return None


def do_export_workflow(workflow, selected_actions=None):
    """
    Proceed with the workflow export.
    :param workflow: Workflow record to export
    be included.
    :param selected_actions: A subset of actions to export
    :return: Page that shows a confirmation message and starts the download
    """

    # Create the context object for the serializer
    context = {'selected_actions': selected_actions}

    # Get the info to send from the serializer
    serializer = WorkflowExportSerializer(workflow, context=context)
    to_send = JSONRenderer().render(serializer.data)

    # Get the in-memory file to compress
    zbuf = cStringIO.StringIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(to_send)
    zfile.close()

    # Attach the compressed value to the response and send
    compressed_content = zbuf.getvalue()
    response = HttpResponse(compressed_content)
    response['Content-Encoding'] = 'application/gzip'
    response['Content-Disposition'] = \
        'attachment; filename="ontask_workflow.gz"'
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
    pandas_db.df_drop_column(workflow.id, column.name)

    # Delete the column
    column.delete()

    # Update the information in the workflow
    workflow.ncols = workflow.ncols - 1
    workflow.save()

    if not cond_to_delete:
        # The conditions to delete are not given, so calculate them
        # Get the conditions/actions attached to this workflow
        cond_to_delete = [x for x in Condition.objects.filter(
            action__workflow=workflow)
                          if formula_evaluation.has_variable(x.formula,
                                                             column.name)]

    # If a column disappears, the conditions that contain that variable
    # are removed..
    for condition in cond_to_delete:
        # Formula has the name of the deleted column.
        # Solution 1: Nuke (Very easy)
        # Solution 2: Mark as invalid and enhance the edit condition form
        #  to handle renaming the fields in a formula (Complex)
        #
        # Solution 1 chosen.
        condition.delete()

    return


def clone_column(column, new_workflow=None, new_name=None):
    """
    Function that given a column clones it and changes workflow and name
    :param column: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """
    # Store the old object name before squashing it
    old_id = column.id
    old_name = column.name

    # Clone
    column.id = None

    # Update some of the fields
    if new_name:
        column.name = new_name
    if new_workflow:
        column.workflow = new_workflow

    # Update
    column.save()

    # Add the column to the table and update it.
    data_frame = pandas_db.load_from_db(column.workflow.id)
    data_frame[new_name] = data_frame[old_name]
    ops.store_dataframe_in_db(data_frame, column.workflow.id)

    return column
