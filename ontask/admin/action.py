# -*- coding: utf-8 -*-

"""Admin definitions for action."""
from django.contrib import admin

from ontask import models


@admin.register(models.Action)
class ActionAdmin(admin.ModelAdmin):
    """Define Action Admin."""

    date_hierarchy = 'modified'

    list_display = (
        'id',
        'workflow',
        'name',
        'description_text',
        'created',
        'modified',
        'text_content',
        'serve_enabled',
    )

    search_fields = [
        'workflow',
        'name',
        'description_text',
        'text_content']
