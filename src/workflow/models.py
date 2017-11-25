# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.dateparse import parse_datetime

from dataops import pandas_db


class Workflow(models.Model):
    """
    Model for a workflow, that is, a matrix, set of column descriptions and
    all the information regarding the actions, conditions and such. This is
    the main object in the relational model.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    name = models.CharField(max_length=512, blank=False)

    description_text = models.CharField(max_length=2048,
                                        default='',
                                        blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Storing the number of rows currently in the data_frame
    nrows = models.IntegerField(verbose_name='Number of rows',
                                default=0,
                                name='nrows',
                                null=False,
                                blank=True)

    # Storing the number of rows currently in the data_frame
    ncols = models.IntegerField(verbose_name='Number of columns',
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
                                    related_name='shared_workflows')

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
                item['values'] = {1: 'Yes', 0: 'No'}
                item['operators'] = ['equal']
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
                item['operators'] = ['equal', 'not_equal']

            result.append(item)

        self.query_builder_ops = result

    def get_query_builder_ops_as_str(self):
        """
        Function to access the query_builder_ops and return it as a string

        :return: Query builder ops structure as string (JSON dumps)
        """
        return json.dumps(self.query_builder_ops)

    def data_frame(self):
        # Function used by the serializer to access the data frame in the DB
        if self.data_frame_table_name:
            return pandas_db.load_from_db(self.id)

        return None

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')


class Column(models.Model):
    """
    """

    # Column name
    name = models.CharField(max_length=512,
                            blank=False,
                            verbose_name='Column name')

    description_text = models.CharField(max_length=2048,
                                        default='',
                                        blank=True)

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 null=False,
                                 blank=False,
                                 related_name='columns')

    # Column type
    data_type = models.CharField(
        max_length=512,
        blank=False,
        null=False,
        choices=[(x, x) for _, x in pandas_db.pandas_datatype_names.items()],
        verbose_name='Type of data to store in the column')

    # Boolean stating if the column is a unique key
    is_key = models.BooleanField(default=False,
                                 verbose_name='Has unique values per row',
                                 null=False,
                                 blank=False)

    # Storing a JSON element with a list of categorical values to use for
    #  this column [val, val, val]
    categories = JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name='Comma separated list of allowed values')

    def get_categories(self):
        """

        :return:
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
                list(set([x.strip() for x in values]))
            )
        else:
            to_store = values

        if self.data_type == 'datetime':
            self.categories = [x.isoformat() for x in to_store]
        else:
            self.categories = to_store

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
            newval = int(value)
        elif data_type == 'double':
            newval = float(value)
        elif data_type == 'boolean':
            newval = value.lower() == 'true' or value == 1
        elif data_type == 'datetime':
            newval = parse_datetime(value)
        else:
            raise ValueError('Unsupported type ' + str(data_type))

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

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'workflow')
        ordering = ('-is_key', 'name')
