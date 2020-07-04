# -*- coding: utf-8 -*-

"""Admin classes for the views."""
from django.contrib import admin

from ontask import models


@admin.register(models.View)
class ViewAdmin(admin.ModelAdmin):
    """Class to admin the views."""

    date_hierarchy = 'modified'

    list_display = (
        'id',
        'workflow',
        'name',
        'description_text',
        'created',
        'modified',
        'formula')

    search_fields = ['workflow', 'name', 'description_text']
