# -*- coding: utf-8 -*-

"""Model description for the Workflow."""

import datetime
import json

from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import pandas as pd

from ontask.dataops.pandas.database import is_table_in_db, load_table
from ontask.dataops.sql import delete_table
from ontask.models.basic import CreateModifyFields, NameAndDescription
from ontask.models.column import Column
from ontask.models.const import CHAR_FIELD_MD5_SIZE
from ontask.models.logs import Log


class Workflow(NameAndDescription, CreateModifyFields):
    """Workflow model.

    Model for a workflow, that is, a table, set of column descriptions and
    all the information regarding the actions, conditions and such. This is
    the main object in the relational model.

    @DynamicAttrs
    """

    table_prefix = '__ONTASK_WORKFLOW_TABLE_'
    df_table_prefix = table_prefix + '{0}'
    upload_table_prefix = table_prefix + 'UPLOAD_{0}'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='workflows_owner')

    # Storing the number of rows currently in the data_frame
    nrows = models.IntegerField(
        verbose_name=_('number of rows'),
        default=0,
        name='nrows',
        null=False,
        blank=True)

    # Storing the number of rows currently in the data_frame
    ncols = models.IntegerField(
        verbose_name=_('number of columns'),
        default=0,
        name='ncols',
        null=False,
        blank=True)

    attributes = JSONField(default=dict, blank=True, null=True)

    query_builder_ops = JSONField(default=dict, blank=True, null=True)

    # Name of the table storing the data frame
    data_frame_table_name = models.CharField(
        max_length=1024,
        default='',
        blank=True)

    # The key of the session locking this workflow (to allow sharing
    # workflows among users
    session_key = models.CharField(
        max_length=CHAR_FIELD_MD5_SIZE,
        default='',
        blank=True)

    # Workflows shared among users. One workflow can be shared with many
    # users, and many users can have this workflow as available to them.
    shared = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='workflows_shared',
        blank=True)

    # Some workflows are marked with a star to appear on top of the collection
    star = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='workflows_star',
        blank=True)

    # Column stipulating where are the learner email values (or empty)
    luser_email_column = models.ForeignKey(
        'Column',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='luser_email_column')

    # MD5 to detect changes in the previous column
    luser_email_column_md5 = models.CharField(
        max_length=CHAR_FIELD_MD5_SIZE,
        default='',
        blank=True)

    lusers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        default=None,
        related_name='workflows_luser')

    # Boolean that flags if the lusers field needs to be updated
    lusers_is_outdated = models.BooleanField(
        default=False,
        null=False,
        blank=False)

    @classmethod
    def unlock_workflow_by_id(cls, wid: int):
        """Remove the session_key from the workflow with given id.

        :param wid: Workflow id
        """
        with cache.lock('ONTASK_WORKFLOW_{0}'.format(wid)):
            try:
                workflow = Workflow.objects.get(id=wid)
                # Workflow exists, unlock
                workflow.unlock()
            except Workflow.DoesNotExist:
                return
            except Exception:
                raise Exception('Unable to unlock workflow {0}'.format(wid))

    def data_frame(self) -> pd.DataFrame:
        """Access the data frame by the serializer."""
        return load_table(self.get_data_frame_table_name())

    def get_data_frame_table_name(self) -> str:
        """Get the table name containing the data frame.

        It updates the field if not present.
        :return: The table name to store the data frame
        """
        if not self.data_frame_table_name:
            self.data_frame_table_name = self.df_table_prefix.format(self.id)
            self.save()
        return self.data_frame_table_name

    def get_upload_table_name(self):
        """Get table name used for temporary data upload.

        :return: The table name to store the data frame
        """
        if not self.data_frame_table_name:
            self.data_frame_table_name = self.df_table_prefix.format(self.id)
            self.save()
        return self.upload_table_prefix.format(self.id)

    def has_table(self) -> bool:
        """Check if the workflow has a table.

        Boolean stating if there is a table storing a data frame
        :return: True if the workflow has a table storing the data frame
        """
        return is_table_in_db(self.get_data_frame_table_name())

    def get_column_info(self):
        """Access name, data_type and key for all columns.

        :return: List of three lists with column info (name, type, is_unique)
        """
        columns = self.columns.all()
        return [
            [col.name for col in columns],
            [col.data_type for col in columns],
            [col.is_key for col in columns]]

    def get_column_names(self):
        """Access column names.

        :return: List with column names
        """
        return list(self.columns.values_list('name', flat=True))

    def get_column_types(self):
        """Access column types.

        :return: List with column types
        """
        return list(self.columns.values_list('data_type', flat=True))

    def get_column_unique(self):
        """Access the is_key values of all the columns.

        :return: List with is_key value for all columns.
        """
        return list(self.columns.values_list('is_key', flat=True))

    def get_unique_columns(self):
        """Get the unique columns.

        :return: Column list.
        """
        return self.columns.filter(is_key=True)

    def set_query_builder_ops(self):
        """Update the jason object with operator and names for the columns.

        Example:

        [{id: 'FIELD1', type: 'string'}, {id: 'FIELD2', type: 'integer'}]
        """
        json_value = []
        for column in self.columns.all():
            op_item = {'id': column.name, 'type': column.data_type}

            # Deal first with the Boolean columns
            if column.data_type == 'boolean':
                op_item['type'] = 'string'
                op_item['input'] = 'select'
                op_item['values'] = ['true', 'false']
                op_item['operators'] = [
                    'equal',
                    'not_equal',
                    'is_null',
                    'is_not_null']
                json_value.append(op_item)
                continue

            # Remaining cases
            if column.data_type == 'double':
                # Double field needs validation field to bypass browser forcing
                # integer
                op_item['validation'] = {'step': 'any'}

            if column.get_categories():
                op_item['input'] = 'select'
                op_item['values'] = column.get_categories()
                op_item['operators'] = [
                    'equal',
                    'not_equal',
                    'is_null',
                    'is_not_null']
            # TODO: Filter is_null and is_not_null out of string columns if
            # NULL values are avoided.

            json_value.append(op_item)

        self.query_builder_ops = json_value

    def get_query_builder_ops_as_str(self) -> str:
        """Obtain the query builder operands as a string.

        :return: Query builder ops structure as string (JSON dumps)
        """
        return json.dumps(self.query_builder_ops)

    def has_data_frame(self) -> bool:
        """Check if a workflow has data frame.

        :return: If the workflow has a dataframe
        """
        return is_table_in_db(self.get_data_frame_table_name())

    def is_locked(self) -> bool:
        """Check if the workflow is locked.

        :return: Is the given workflow locked?
        """
        if not self.session_key:
            # No key in the workflow, then it is not locked.
            return False

        session = Session.objects.filter(session_key=self.session_key).first()
        if not session:
            # Session does not exist, then it is not locked
            return False

        # Session is in the workflow and in the session table. Locked if expire
        # date is beyond the current time.
        return session.expire_date >= timezone.now()

    def lock(self, request: http.HttpRequest, create_session: bool = False):
        """Set a session key in the workflow to set is as locked.

        :param request: HTTP request

        :param create_session: Boolean to flag if a new session has to be
               created.

        :return: The session_key is assigned and saved.
        """
        if request.session.session_key is not None:
            # Trivial case, the request has a legit session, so use it for
            # the lock.
            self.session_key = request.session.session_key
            self.save()

        # The request has a temporary session (non persistent). This is the
        # case when the API is invoked. There are four possible case:
        #
        # Case 1: The workflow has empty lock information: CREATE SESSION and
        #  UPDATE
        #
        # Case 2: The workflow has a session, but is not in the DB: CREATE
        # SESSION and UPDATE
        #
        # Case 3: The workflow has a session but it has expired: UPDATE THE
        # EXPIRE DATE OF THE SESSION
        #
        # Case 4: The workflow has a perfectly valid session: UPDATE THE
        # EXPIRE DATE OF THE SESSION
        #
        if create_session:
            # Cases 1 and 2. Create a session and store the user_id
            request.session['_auth_user_id'] = request.user.id
            request.session.save()
            self.session_key = request.session.session_key
            self.save()
            return

        # Cases 3 and 4. Update the existing session
        session = Session.objects.get(pk=self.session_key)
        session.expire_date = timezone.now() + datetime.timedelta(
            seconds=settings.SESSION_COOKIE_AGE)
        session.save()

    def unlock(self):
        """Remove the session_key from the workflow.

        :return: Nothing
        """
        self.session_key = ''
        self.save()

    def get_user_locking_workflow(self):
        """Get the user that is locking a workflow.

        Given a workflow that is supposed to be locked, it returns the user
        that is locking it.

        :return: The user object that is locking this workflow
        """
        session = Session.objects.get(session_key=self.session_key)
        session_data = session.get_decoded()
        return get_user_model().objects.get(
            id=session_data.get('_auth_user_id'))

    def flush(self):
        """Flush all the data from the workflow and propagate changes.

        It removes relations with columns, conditions, filters, etc. These
        steps require:

        1) Delete the data frame from the database

        2) Delete all the actions attached to the workflow (with their
        conditions)

        3) Delete all the views attached to the workflow

        4) Delete all the columns attached to the workflow

        :return: Reflected in the DB
        """
        # Step 1: Delete the data frame from the database
        delete_table(self.get_data_frame_table_name())

        # Reset some of the workflow fields
        self.nrows = 0
        self.ncols = 0
        self.n_filterd_rows = -1
        self.data_frame_table_name = ''

        # Step 2: Delete the conditions attached to all the actions attached
        # to the workflow.
        for act in self.actions.all():
            act.conditions.all().delete()
            act.delete()

        # Step 3: Delete all the views attached to the workflow
        self.views.all().delete()

        # Step 4: Delete the column_names, column_types and column_unique
        self.columns.all().delete()
        self.set_query_builder_ops()

        # Save the workflow with the new fields.
        self.save()

    def add_columns(self, triplets):
        """Add a set of columns to the workflow.

        :param triplets: List of (column name, data type, is_key)

        :return: Nothing. Create objects in the workflow.
        """
        bulk_list = []
        position = self.ncols
        for cname, dtype, is_key in triplets:
            position += 1
            # Create the new column
            bulk_list.append(Column(
                name=cname,
                workflow=self,
                data_type=dtype,
                is_key=is_key,
                position=position))
        Column.objects.bulk_create(bulk_list)
        self.ncols = position
        self.save()

    def reposition_columns(self, from_idx, to_idx):
        """Relocate the columns from one index to another.

        :param from_idx: Position from which the column is repositioned.

        :param to_idx: New position for the column

        :return: Nothing. Column is repositioned.
        """
        # If the indeces are identical, nothing needs to be moved.
        if from_idx == to_idx:
            return

        if from_idx < to_idx:
            cols = self.columns.filter(
                position__gt=from_idx,
                position__lte=to_idx)
            step = -1
        else:
            cols = self.columns.filter(
                position__gte=to_idx,
                position__lt=from_idx)
            step = 1

        # Update the positions of the appropriate columns
        for col in cols:
            col.position = col.position + step
            col.save()

    def __str__(self) -> str:
        """Render as string."""
        return self.name

    def log(self, user, operation_type: str, **kwargs: str):
        """Log the operation with the object."""
        payload = {
            'name': self.name,
            'ncols': self.ncols,
            'nrows': self.nrows,
            'star': self.user in self.star.all()}

        payload.update(kwargs)
        return Log.objects.register(user, operation_type, self, payload)

    class Meta:
        """Define verbose and unique together."""

        verbose_name = 'workflow'
        verbose_name_plural = 'workflows'
        unique_together = ('user', 'name')
