# -*- coding: utf-8 -*-

"""Admin apps to manage workflows."""

from django.contrib import admin

from ontask.models import Workflow


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


admin.site.register(Workflow, WorkflowAdmin)
