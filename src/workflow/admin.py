# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import Workflow, Column


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'description_text',
                    'created',
                    'modified',
                    'attributes',
                    'nrows',
                    'ncols',
                    'query_builder_ops',
                    'data_frame_table_name',
                    'session_key')

    filter_horizontal = ('shared',)


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'data_type',
                    'is_key',
                    'categories',
                    'workflow')


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Column, ColumnAdmin)
