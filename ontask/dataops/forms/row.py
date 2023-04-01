"""Forms to introduce values for a row in the data frame."""
from django import forms

from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX, column_to_field


class RowForm(forms.Form):
    """Form to enter values for a table row."""

    def __init__(self, *args, **kargs):
        """Initialize form based on list of columns."""
        # Store the instance
        self.workflow = kargs.pop('workflow', None)
        self.columns = self.workflow.columns.all()
        self.initial_values = kargs.pop('initial_values', {})

        super().__init__(*args, **kargs)

        if not self.workflow:
            return

        for idx, column in enumerate(self.columns):
            col_val = self.initial_values.get(column.name)
            field = column_to_field(column, col_val)

            if column.is_key:
                if col_val:
                    field.widget.attrs['readonly'] = 'readonly'
                else:
                    field.required = True
            elif column.data_type == 'integer':
                field.required = True

            self.fields[ONTASK_UPLOAD_FIELD_PREFIX + '%s' % idx] = field
