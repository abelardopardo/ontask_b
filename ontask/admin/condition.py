"""Admin for Conditions."""
from django.contrib import admin

from ontask import models


@admin.register(models.Condition)
class ConditionAdmin(admin.ModelAdmin):
    """Define Condition Admin."""

    list_display = (
        'id',
        'name',
        'action',
        'description_text',
        '_formula',
        'selected_count')

    search_fields = ['name', 'action', 'description_text']

@admin.register(models.Filter)
class FilterAdmin(admin.ModelAdmin):
    """Define Filter Admin."""

    list_display = (
        'id',
        'description_text',
        '_formula',
        'selected_count')

    search_fields = ['description_text']
