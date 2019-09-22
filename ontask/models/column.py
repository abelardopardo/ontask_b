# -*- coding: utf-8 -*-

"""Column model."""

import datetime

import pytz
from django.conf import settings
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _

import ontask.dataops.pandas.datatypes
from ontask.models.const import CHAR_FIELD_LONG_SIZE, CHAR_FIELD_MID_SIZE


class Column(models.Model):
    """Column object.

    Contains information that should be at all times consistent with the
    structure of the data frame stored in the database.

    The column must point to the workflow.

    Some columns are identified as "key" if they have unique values for all
    table rows (pandas takes care of this with one line of code)

    The data type is computed by Pandas upon reading the data.

    The categories field is to provide a finite set of values as a JSON list

    @DynamicAttrs
    """

    # Column name
    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=False,
        verbose_name=_('column name'))

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'))

    workflow = models.ForeignKey(
        'Workflow',
        db_index=True,
        editable=False,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='columns')

    # Column type
    data_type = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=False,
        choices=[
            (dtype, dtype)
            for __, dtype in list(
                ontask.dataops.pandas.datatypes.pandas_datatype_names.items())],
        verbose_name=_('type of data to store in the column'))

    # Boolean stating if the column is a unique key
    is_key = models.BooleanField(
        default=False,
        verbose_name=_('has unique values per row'),
        null=False,
        blank=False)

    # Position of the column in the workflow table
    position = models.IntegerField(
        verbose_name=_('column position (zero to insert last)'),
        default=0,
        name='position',
        null=False,
        blank=False)

    # Boolean stating if the column is included in the visualizations
    in_viz = models.BooleanField(
        default=True,
        verbose_name=_('include in visualization'),
        null=False,
        blank=False)

    # Storing a JSON element with a list of categorical values to use for
    #  this column [val, val, val]
    categories = JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('comma separated list of values allowed'))

    # Validity window
    active_from = models.DateTimeField(
        _('Column active from'),
        blank=True,
        null=True,
        default=None)

    active_to = models.DateTimeField(
        _('Column active until'),
        blank=True,
        null=True,
        default=None)

    def get_categories(self):
        """Return the categories and parse datetime if needed.

        :return: List of values
        """
        if self.data_type == 'datetime':
            return [parse_datetime(cat) for cat in self.categories]

        return self.categories

    def set_categories(self, cat_values, validate=False):
        """Set the categories available in a column.

        The function checks that the values are compatible with the declared
        column type. There is a special case with datetime objects, because
        they are not JSON serializable. In that case, they are translated to
        the ISO 8601 string format and stored.

        :param cat_values: List of category values

        :param validate: Boolean to enable validation of the given values

        :return: Nothing. Sets the value in the object
        """
        # Calculate the values to store
        if validate:
            to_store = self.validate_column_values(
                self.data_type,
                [cat_value.strip() for cat_value in cat_values])
        else:
            to_store = cat_values

        if self.data_type == 'datetime':
            self.categories = [cat_val.isoformat() for cat_val in to_store]
        else:
            self.categories = to_store

    def get_simplified_data_type(self):
        """Get a data type name to show to users.

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
        """Recalculate the position of this column.

        :param to_idx: Destination index of the given column
        :return: Content reflected in the DB
        """
        self.workflow.reposition_columns(self.position, to_idx)
        self.position = to_idx
        self.save()

    @classmethod
    def validate_column_value(cls, data_type, col_value):
        """Check if a value is correct for a column.

        Test that a value is suitable to be stored in this column. It is done
         simply by casting the type and throwing the corresponding exception.

        :param data_type: string specifying the data type

        :param col_value: Value to store in the column

        :return: The new value to be stored
        """
        # Remove spaces
        col_value = col_value.strip()

        distrib = {
            'string': lambda txt_val: str(txt_val),
            'double': lambda txt_val: float(txt_val),
            'boolean': lambda txt_val: (
                txt_val.lower() == 'true' or txt_val == 1),
            'datetime': lambda txt_val: parse_datetime(txt_val),
            'integer': None,
        }

        if data_type not in distrib.keys():
            raise ValueError(
                _('Unsupported type %(type)s') % {'type': str(data_type)})

        if data_type == 'integer':
            # In this case, although the column has been declared as an
            # integer, it could mutate to a float, so we allow this value.
            try:
                newval = int(col_value)
            except ValueError:
                newval = float(col_value)
        else:
            newval = distrib[data_type](col_value)

        return newval

    @classmethod
    def validate_column_values(cls, data_type, col_values):
        """Check if column values are valid.

        Test that a list of values are suitable to be stored in this column.
        It is done simply by casting the type to each element and throwing the
        corresponding exception.

        :param data_type: string specifying the data type

        :param col_values: List of values to store in the column

        :return: The new values to be stored
        """
        return [
            Column.validate_column_value(data_type, col_val)
            for col_val in col_values]

    @property
    def is_active(self):
        """Check if a column is active.

        The current time is within the
        interval defined by active_from - active_to.

        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not (
            (self.active_from and now < self.active_from)
            or (self.active_to and self.active_to < now))

    def __str__(self):
        """Render as string."""
        return self.name

    def __unicode__(self):
        """Render as unicode."""
        return self.name

    class Meta:
        """Define additional fields, unique criteria and ordering."""

        verbose_name = 'column'
        verbose_name_plural = 'columns'
        unique_together = ('name', 'workflow')
        ordering = ['position']
