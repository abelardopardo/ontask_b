"""Generic table elements for django-tables2 package."""
from django.template.loader import render_to_string
import django_tables2 as tables


class OperationsColumn(tables.Column):
    """Column showing operations over the element in the row."""

    def __init__(self, *args, **kwargs):
        """Set the fields from kwargs and empty values."""
        self.template_file = kwargs.pop('template_file')
        self.template_context = kwargs.pop('template_context')

        super().__init__(*args, **kwargs)

        self.empty_values = []

    def render(self, record) -> str:
        """Render the column using the template."""
        return render_to_string(
            self.template_file,
            self.template_context(record))


class BooleanColumn(tables.Column):
    """Column showing boolean values with tick/cross."""

    def __init__(self, *args, **kwargs):
        """Get the field name."""
        self.get_field = kwargs.pop('get_field')
        super().__init__(*args, **kwargs)

    def render(self, record):
        """Render tick and cross."""
        return '✔' if self.get_field(record) else '✘'


class DataTablesServerSidePaging:
    """Class to handle DataTables Server Side Paging request.

    For large tables DataTables allows to preload a subset of a table
    that is requested through AJAX. These requests arrive with a set of
    paging parameters that are stored in these objects.
    """

    draw: int = 0
    start: int = 0
    order_column = None
    order_direction = None
    search_value = None
    is_valid = True

    def __init__(self, request_data):
        """Extract the data from the request."""
        try:
            self.draw = int(request_data.POST.get('draw'))
            self.start = int(request_data.POST.get('start'))
            self.length = int(request_data.POST.get('length'))
            self.order_col = request_data.POST.get('order[0][column]')
            self.order_dir = request_data.POST.get('order[0][dir]', 'asc')
            self.search_value = request_data.POST.get('search[value]')
        except ValueError:
            self.is_valid = False

        if self.order_col:
            self.order_col = int(self.order_col)
