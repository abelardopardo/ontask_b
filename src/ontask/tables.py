# -*- coding: utf-8 -*-

"""Generic table elements for django-tables2 package."""

import django_tables2 as tables
from django.template.loader import render_to_string


class OperationsColumn(tables.Column):
    """Column showing operations over the element in the row."""

    def __init__(self, *args, **kwargs):
        """Set the fields from kwargs and empty values."""
        self.template_file = kwargs.pop('template_file')
        self.template_context = kwargs.pop('template_context')

        super().__init__(*args, **kwargs)

        self.empty_values = []

    def render(self, record, table):
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

    def render(self, record, table):
        """Render tick and cross."""
        return '✔' if self.get_field(record) else '✘'
