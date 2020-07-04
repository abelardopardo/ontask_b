# -*- coding: utf-8 -*-

"""Admin apps to manage workflows."""
from django.contrib import admin

from ontask import models


@admin.register(models.Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Workflow admin app."""

    date_hierarchy = 'modified'

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

    search_fields = [
        'name',
        'description_text',
        'attributes',
        'query_builder_ops',
        'data_frame_table_name',
        'session_key']

    filter_horizontal = ('shared',)
