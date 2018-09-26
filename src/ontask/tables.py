# -*- coding: utf-8 -*-


import django_tables2 as tables
from django.template.loader import render_to_string


class OperationsColumn(tables.Column):
    empty_values = []

    def __init__(self, *args, **kwargs):
        self.template_file = kwargs.pop('template_file')
        self.template_context = kwargs.pop('template_context')

        super(OperationsColumn, self).__init__(*args, **kwargs)

    def render(self, record, table):
        return render_to_string(self.template_file,
                                self.template_context(record))


class BooleanColumn(tables.Column):

    def __init__(self, *args, **kwargs):
        self.get_field = kwargs.pop('get_field')
        super(BooleanColumn, self).__init__(*args, **kwargs)

    def render(self, record, table):
        return '✔' if self.get_field(record) else '✘'