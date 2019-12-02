# -*- coding: utf-8 -*-

"""Admin apps to manage columns."""
from django.contrib import admin

from ontask import models


@admin.register(models.Column)
class ColumnAdmin(admin.ModelAdmin):
    """Column Admin app."""

    list_display = (
        'id',
        'name',
        'data_type',
        'is_key',
        'categories',
        'workflow')
