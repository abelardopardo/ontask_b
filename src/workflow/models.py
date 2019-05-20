# -*- coding: utf-8 -*-


import datetime
import json
from builtins import object, str

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, models
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _

import ontask.templatetags.ontask_tags
from dataops.pandas import pandas_datatype_names, load_table
from dataops.sql import delete_table


class Workflow(models.Model):
    """
    Model for a workflow, that is, a table, set of column descriptions and
    all the information regarding the actions, conditions and such. This is
    the main object in the relational model.
    """

    table_prefix = '__ONTASK_WORKFLOW_TABLE_'
    df_table_prefix = table_prefix + '{0}'
    upload_table_prefix = table_prefix + 'UPLOAD_{0}'

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='workflows_owner')

    name = models.CharField(max_length=512, null=False, blank=False)

    description_text = models.CharField(max_length=2048,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Storing the number of rows currently in the data_frame
    nrows = models.IntegerField(verbose_name=_('number of rows'),
                                default=0,
                                name='nrows',
                                null=False,
                                blank=True)

    # Storing the number of rows currently in the data_frame
    ncols = models.IntegerField(verbose_name=_('number of columns'),
                                default=0,
                                name='ncols',
                                null=False,
                                blank=True)

    attributes = JSONField(default=dict,
                           blank=True,
                           null=True)

    query_builder_ops = JSONField(default=dict,
                                  blank=True,
                                  null=True)

    # Name of the table storing the data frame
    data_frame_table_name = models.CharField(max_length=1024,
                                             default='',
                                             null=False,
                                             blank=True)

    # The key of the session locking this workflow (to allow sharing
    # workflows among users
    session_key = models.CharField(max_length=40,
                                   default='',
                                   null=False,
                                   blank=True)

    # Workflows shared among users. One workflow can be shared with many
    # users, and many users can have this workflow as available to them.
    shared = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                    related_name='workflows_shared')

    # Column stipulating where are the learner email values (or empty)
    luser_email_column = models.ForeignKey('Column',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           blank=False,
                                           related_name='luser_email_column')

    # MD5 to detect changes in the previous column
    luser_email_column_md5 = models.CharField(max_length=32,
                                              default='',
                                              null=False,
                                              blank=True)

    lusers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                    default=None,
                                    related_name='workflows_luser')

    # Boolean that flags if the lusers field needs to be updated
    lusers_is_outdated = models.BooleanField(
        default=False,
        null=False,
        blank=False)

    @staticmethod
    def unlock_workflow_by_id(wid):
        """
        Removes the session_key from the workflow with given id
        :param wid: Workflow id
        :return:
        """
        with cache.lock('ONTASK_WORKFLOW_{0}'.format(wid)):
            try:
                workflow = Workflow.objects.get(id=wid)

                # Workflow exists, unlock
                workflow.unlock()
            except ObjectDoesNotExist:
                return
            except Exception:
                raise Exception('Unable to unlock workflow {0}'.format(wid))

    def data_frame(self):
        # Function used by the serializer to access the data frame in the DB
        return load_table(self.get_data_frame_table_name())

    def get_data_frame_table_name(self):
        """
        Function to get the data_frame_table_name and update it in case it is
        empty in the DB
        :return: The table name to store the data frame
        """
        if not self.data_frame_table_name:
            self.data_frame_table_name = self.df_table_prefix.format(self.id)
            self.save()
        return self.data_frame_table_name

    def get_data_frame_upload_table_name(self):
        """
        Function to get the table name for the upload data frame and update
        data_frame_table_name if empty.
        :return: The table name to store the data frame
        """
        if not self.data_frame_table_name:
            self.data_frame_table_name = self.df_table_prefix.format(self.id)
            self.save()
        return self.upload_table_prefix.format(self.id)

    def has_table(self):
        """
        Boolean stating if there is a table storing a data frame
        :return: True if the workflow has a table storing the data frame
        """

        return is_table_in_db(self.get_data_frame_table_name())

    def get_columns(self):
        """
        Function to access the Columns

        :return: List with columns
        """

        return self.columns.all()

    def get_column_info(self):
        """
        :return: List of three lists with column info (name, type, is_unique)
        """

        columns = self.get_columns()
        return [[x.name for x in columns],
                [x.data_type for x in columns],
                [x.is_key for x in columns]]

    def get_column_names(self):
        """
        Function to access the Column names.

        :return: List with column names
        """

        return list(self.columns.all().values_list('name', flat=True))

    def get_column_types(self):
        """
        Function to access the Column types.

        :return: List with column types
        """

        return list(self.columns.all().values_list('data_type', flat=True))

    def get_column_unique(self):
        """
        Function to access the Column unique.

        :return: List with column types
        """
        return list(self.columns.all().values_list('is_key', flat=True))

    def get_unique_columns(self):
        """
        Function to access the Column unique.

        :return: List with column types
        """
        return self.columns.filter(is_key=True)

    def set_query_builder_ops(self):
        """
        Update the JS structure with the initial operators and names for the
        columns

        Example:

        [{id: 'FIELD1', type: 'string'}, {id: 'FIELD2', type: 'integer'}]
        """

        result = []
        for column in self.columns.all():
            item = {'id': column.name, 'type': column.data_type}

            # Deal first with the Boolean columns
            if column.data_type == 'boolean':
                # Boolean will only use EQUAL and Yes/No as choices
                item['input'] = 'radio'
                item['values'] = {True: 'Yes', False: 'No'}
                item['operators'] = ['equal', 'is_null', 'is_not_null']
                result.append(item)
                continue

            # Remaining cases
            if column.data_type == 'double':
                # Double field needs validation field to bypass browser forcing
                # integer
                item['validation'] = {'step': 'any'}

            if column.get_categories():
                item['input'] = 'select'
                item['values'] = column.get_categories()
                item['operators'] = ['equal',
                                     'not_equal',
                                     'is_null',
                                     'is_not_null']

            result.append(item)

        self.query_builder_ops = result

    def get_query_builder_ops_as_str(self):
        """
        Function to access the query_builder_ops and return it as a string

        :return: Query builder ops structure as string (JSON dumps)
        """
        return json.dumps(self.query_builder_ops)

    def version(self):
        """
        Function that simply returns the platform version (function used by
        the serializer
        :return: the platform version
        """
        return ontask.templatetags.ontask_tags.ontask_version()

    def has_data_frame(self):
        """
        :return: If the workflow has a dataframe
        """
        return is_table_in_db(self.get_data_frame_table_name())

    def is_locked(self):
        """
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

    def lock(self, request, create_session=False):
        """
        Function that sets the session key in the workflow to flag that is
        locked.
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
        """
        Removes the session_key from the workflow
        :return: Nothing
        """
        self.session_key = ''
        self.save()

    def get_user_locking_workflow(self):
        """
        Given a workflow that is supposed to be locked, it returns the user that
        is locking it.
        :return: The user object that is locking this workflow
        """
        session = Session.objects.get(session_key=self.session_key)
        session_data = session.get_decoded()
        return get_user_model().objects.get(
            id=session_data.get('_auth_user_id'))

    def flush(self):
        """
        Flush all the data from the workflow and propagate changes throughout
        the relations with columns, conditions, filters, etc. These steps
        require:

        1) Delete the data frame from the database

        2) Delete all the columns attached to the workflow

        3) Delete all the conditions attached to the actions

        4) Delete all the views attached to the workflow

        :return: Reflected in the DB
        """

        # Step 1: Delete the data frame from the database
        delete_table(self.get_data_frame_table_name())

        # Reset some of the workflow fields
        self.nrows = 0
        self.ncols = 0
        self.n_filterd_rows = -1
        self.set_query_builder_ops()
        self.data_frame_table_name = ''

        # Step 2: Delete the column_names, column_types and column_unique
        self.columns.all().delete()

        # Step 3: Delete the conditions attached to all the actions attached
        # to the workflow.
        self.actions.all().delete()

        # Step 4: Delete all the views attached to the workflow
        self.views.all().delete()

        # Save the workflow with the new fields.
        self.save()

    def add_new_columns(self, col_names, data_types, are_keys):
        """Add a set of columns to the workflow"""
        start = self.columns.count() + 1
        bulk_list = []
        for idx in range(len(col_names)):
            # Create the new column
            bulk_list.append(Column(
                name=col_names[idx],
                workflow=self,
                data_type=pandas_datatype_names.get(data_types[idx]),
                is_key=are_keys[idx],
                position=start + idx))
            idx += 1
        Column.objects.bulk_create(bulk_list)

    def reposition_columns(self, from_idx, to_idx):
        """

        :param from_idx: Position from which the column is repositioned.
        :param to_idx: New position for the column
        :return: Appropriate column positions are modified
        """

        # If the indeces are identical, nothing needs to be moved.
        if from_idx == to_idx:
            return

        if from_idx < to_idx:
            cols = self.columns.filter(position__gt=from_idx,
                                       position__lte=to_idx)
            step = -1
        else:
            cols = self.columns.filter(position__gte=to_idx,
                                       position__lt=from_idx)
            step = 1

        # Update the positions of the appropriate columns
        for col in cols:
            col.position = col.position + step
            col.save()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = 'workflow'
        verbose_name_plural = 'workflows'
        unique_together = ('user', 'name')


class Column(models.Model):
    """
    Column object. contains information that should be at all times
    consistent with the structure of the data frame stored in the database.

    The column must point to the workflow.

    Some columns are identified as "key" if they have unique values for all
    table rows (pandas takes care of this with one line of code)

    The data type is computed by Pandas upon reading the data.

    The categories field is to provide a finite set of values as a JSON list

    """

    # Column name
    name = models.CharField(max_length=512,
                            blank=False,
                            verbose_name=_('column name'))

    description_text = models.CharField(
        max_length=2048,
        default='',
        blank=True,
        verbose_name=_('description')
    )

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 editable=False,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name='columns')

    # Column type
    data_type = models.CharField(
        max_length=512,
        blank=False,
        null=False,
        choices=[(x, x)
                 for __, x in list(pandas_datatype_names.items())],
        verbose_name=_('type of data to store in the column')
    )

    # Boolean stating if the column is a unique key
    is_key = models.BooleanField(default=False,
                                 verbose_name=_('has unique values per row'),
                                 null=False,
                                 blank=False)

    # Position of the column in the workflow table
    position = models.IntegerField(
        verbose_name=_('column position (zero to insert last)'),
        default=0,
        name='position',
        null=False,
        blank=False
    )

    # Boolean stating if the column is included in the visualizations
    in_viz = models.BooleanField(default=True,
                                 verbose_name=_('include in visualization'),
                                 null=False,
                                 blank=False)

    # Storing a JSON element with a list of categorical values to use for
    #  this column [val, val, val]
    categories = JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('comma separated list of values allowed')
    )

    # Validity window
    active_from = models.DateTimeField(
        _('Column active from'),
        blank=True,
        null=True,
        default=None,
    )

    active_to = models.DateTimeField(
        _('Column active until'),
        blank=True,
        null=True,
        default=None
    )

    def get_categories(self):
        """
        Return the categories and parse datetime if needed.
        :return: List of values
        """
        if self.data_type == 'datetime':
            return [parse_datetime(x) for x in self.categories]

        return self.categories

    def set_categories(self, values, validate=False):
        """
        Set the categories available in a column. The function checks that
        the values are compatible with the declared column type. There is a
        special case with datetime objects, because they are not JSON
        serializable. In that case, they are translated to the ISO 8601
        string format and stored.

        :param values: List of category values
        :param validate: Boolean to enable validation of the given values
        :return: Nothing. Sets the value in the object
        """
        # Calculate the values to store
        if validate:
            to_store = self.validate_column_values(
                self.data_type,
                [x.strip() for x in values]
            )
        else:
            to_store = values

        if self.data_type == 'datetime':
            self.categories = [x.isoformat() for x in to_store]
        else:
            self.categories = to_store

    def get_simplified_data_type(self):
        """
        :return: The simplified data type using "number" for either integer or
        double
        """
        if self.data_type == 'string':
            return 'Text'

        if self.data_type == 'integer' or self.data_type == 'double':
            return 'Number'

        if self.data_type == 'datetime':
            return 'Date and time'

        if self.data_type == 'boolean':
            return 'True/False'

        raise Exception('Unexpected data type {0}'.format(self.data_type))

    def reposition_and_update_df(self, to_idx):
        """

        :param to_idx: Destination index of the given column
        :return: Content reflected in the DB
        """

        self.workflow.reposition_columns(self.position, to_idx)
        self.position = to_idx
        self.save()

    @staticmethod
    def validate_column_value(data_type, value):
        """
        Test that a value is suitable to be stored in this column. It is done
         simply by casting the type and throwing the corresponding exception.
        :param data_type: string specifying the data type
        :param value: Value to store in the column
        :return: The new value to be stored
        """

        # Remove spaces
        value = value.strip()

        # Check the different data types
        if data_type == 'string':
            newval = str(value)
        elif data_type == 'integer':
            # In this case, although the column has been declared as an
            # integer, it could mutate to a float, so we allow this value.
            try:
                newval = int(value)
            except ValueError:
                newval = float(value)
        elif data_type == 'double':
            newval = float(value)
        elif data_type == 'boolean':
            newval = value.lower() == 'true' or value == 1
        elif data_type == 'datetime':
            newval = parse_datetime(value)
        else:
            raise ValueError(
                _('Unsupported type %(type)s') % {'type': str(data_type)}
            )

        return newval

    @staticmethod
    def validate_column_values(data_type, values):
        """
        Test that a list of values are suitable to be stored in this column.
        It is done simply by casting the type to each element and throwing the
        corresponding exception.
        :param data_type: string specifying the data type
        :param values: List of values to store in the column
        :return: The new values to be stored
        """

        return [Column.validate_column_value(data_type, x) for x in values]

    @property
    def is_active(self):
        """
        Function to ask if a column is active: the current time is within the
        interval defined by active_from - active_to.
        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not ((self.active_from and now < self.active_from) or
                    (self.active_to and self.active_to < now))

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = 'column'
        verbose_name_plural = 'columns'
        unique_together = ('name', 'workflow')
        ordering = ['position',]


def is_table_in_db(table_name: str) -> bool:
    with connection.cursor() as cursor:
        return next(
            (True for x in connection.introspection.get_table_list(cursor)
             if x.name == table_name),
            False
        )
