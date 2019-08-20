# -*- coding: utf-8 -*-

"""Admin apps to manage workflows and columns."""

from django.contrib import admin

from ontask.models import Column, Workflow


class WorkflowAdmin(admin.ModelAdmin):
    """Workflow admin app."""

    list_display = (
        'id',
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
    """Column Admin app."""

    list_display = (
        'id',
        'name',
        'data_type',
        'is_key',
        'categories',
        'workflow')


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Column, ColumnAdmin)
