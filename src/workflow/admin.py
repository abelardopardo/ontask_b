# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Workflow


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'description_text',
                    'created',
                    'attributes',
                    'nrows',
                    'ncols',
                    'column_names',
                    'column_types',
                    'column_unique',
                    'query_builder_ops',
                    'data_frame_table_name')


admin.site.register(Workflow, WorkflowAdmin)
