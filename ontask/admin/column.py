# -*- coding: utf-8 -*-

"""Admin apps to manage columns."""

from django.contrib import admin

from ontask.models import Column


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    """Column Admin app."""

    list_display = (
        'id',
        'name',
        'data_type',
        'is_key',
        'categories',
        'workflow')

