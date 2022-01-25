# -*- coding: utf-8 -*-

"""Column model."""
import datetime
from typing import Any, List, Optional, Tuple

from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
import pytz

from ontask.dataops import pandas, sql
from ontask.models.common import CHAR_FIELD_MID_SIZE, NameAndDescription
from ontask.models.logs import Log


class Column(NameAndDescription):
    """Column object.

    Contains information that should be at all times consistent with the
    structure of the data frame stored in the database.

    The column must point to the workflow.

    Some columns are identified as "key" if they have unique values for all
    table rows (pandas takes care of this with one line of code)

    The data type is computed by Pandas upon reading the data.

    The categories field is to provide a finite set of values as a JSON report

    @DynamicAttrs
    """

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
            for __, dtype in list(pandas.datatype_names.items())],
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

    def set_categories(
        self,
        cat_values,
        validate_type: Optional[bool] = False,
        update: Optional[bool] = True
    ) -> bool:
        """Set the categories available in a column.

        The function checks that the values are compatible with the declared
        column type. There is a special case with datetime objects, because
        they are not JSON serializable. In that case, they are translated to
        the ISO 8601 string format and stored.

        :param cat_values: List of category values
        :param validate_type: Boolean to enable validation of the given values
        :param update: Boolean to control if the field is updated
        :return: Boolean saying if the update has been successful
        """
        # Calculate the values to store
        if validate_type:
            to_store = self.validate_values_type(
                self.data_type,
                [cat_value.strip() for cat_value in cat_values])
        else:
            to_store = cat_values

        if any(isinstance(elem, datetime.datetime) for elem in cat_values):
            to_store = [cat_val.isoformat() for cat_val in to_store]

        # Update the field in memory
        self.categories = to_store

        if update:
            # Update the field in the DB
            self.save(update_fields=['categories'])
            return True

        return False

    def get_simplified_data_type(self) -> str:
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

    def reposition_and_update_df(self, to_idx: int):
        """Recalculate the position of this column.

        :param to_idx: Destination index of the given column
        :return: Content reflected in the DB
        """
        self.workflow.reposition_columns(self.position, to_idx)
        self.position = to_idx
        self.save(update_fields=['position'])

    @classmethod
    def validate_value_type(cls, data_type, col_value) -> Any:
        """Check if a value is correct for a column.

        Test that a value is suitable to be stored in this column. It is done
         simply by casting the type and throwing the corresponding exception.

        :param data_type: string specifying the data type
        :param col_value: Value to store in the column
        :return: The new value to be stored
        """
        # Remove spaces
        col_value = col_value.strip()

        convert_functions = {
            'string': lambda txt_val: str(txt_val),
            'double': lambda txt_val: float(txt_val),
            'boolean': lambda txt_val: (
                txt_val.lower() == 'true' or txt_val == 1),
            'datetime': lambda txt_val: parse_datetime(txt_val),
            'integer': None,
        }

        if data_type not in convert_functions.keys():
            raise ValueError(
                _('Unsupported type %(type)s') % {'type': str(data_type)})

        if data_type == 'integer':
            # In this case, although the column has been declared as an
            # integer, it could mutate to a float, so we allow this value.
            try:
                new_value = int(col_value)
            except ValueError:
                new_value = float(col_value)
        else:
            new_value = convert_functions[data_type](col_value)

        return new_value

    @classmethod
    def validate_values_type(
        cls,
        data_type: str,
        col_values: List[Any]
    ) -> List[Any]:
        """Check if column values are valid.

        Test that a list of values are suitable to be stored in this column.
        It is done simply by casting the type to each element and throwing the
        corresponding exception.

        :param data_type: string specifying the data type
        :param col_values: List of values to store in the column
        :return: The new values to be stored
        """
        return [
            Column.validate_value_type(data_type, col_val)
            for col_val in col_values]

    def validate_categories(
        self,
        categories: List
    ) -> Tuple[List, Optional[str]]:
        """Check that categories are valid for this column.

        The method checks for the following conditions:

        1. There is more than one category
        2. Categories must be compatible with column type
        3. Categories are compatible with the existing data in the table

        :param categories: List of values to consider in the column
        :return: A pair: list of adjusted values and None if all conditions
        are satisfied, or an empty list and a string with the reason the
        values have not been validated.
        """
        # Condition 1: There must be more than one value
        if len(categories) < 2:
            return [], _('More than a single value needed.')

        # Condition 2: Values must be valid for the type of the column
        try:
            valid_values = self.validate_values_type(self.data_type, categories)
        except (ValueError, KeyError):
            return [], _('Incorrect list of values')

        # Condition 3: The values in the dataframe column must be in
        # these categories
        if self.id:
            # Only needed when column is in DB (avoid new empty columns)
            column_values = sql.get_column_distinct_values(
                self.workflow.get_data_frame_table_name(),
                self.name)
            if not set(column_values).issubset(valid_values):
                return [], _('Column values incompatible with categories.')

        return valid_values, None

    @property
    def is_active(self) -> bool:
        """Check if a column is active.

        The current time is within the
        interval defined by active_from - active_to.

        :return: Boolean encoding the active status
        """
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return not (
            (self.active_from and now < self.active_from)
            or (self.active_to and self.active_to < now))

    def __str__(self) -> str:
        """Render as string."""
        return self.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'type': self.data_type,
            'is_key': self.is_key,
            'position': self.position,
            'categories': self.categories,
            'active_from': self.active_from,
            'active_to': self.active_to,
            'workflow_id': self.workflow_id}

        payload.update(kwargs)
        return Log.objects.register(
            user,
            operation_type,
            self.workflow,
            payload)

    class Meta:
        """Define additional fields, unique criteria and ordering."""

        verbose_name = 'column'
        verbose_name_plural = 'columns'
        unique_together = ('name', 'workflow')
        ordering = ['position']
