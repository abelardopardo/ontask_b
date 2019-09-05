# -*- coding: utf-8 -*-

"""Admin for Conditions."""

from django.contrib import admin

from ontask.models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    """Define Condition Admin."""

    list_display = (
        'id',
        'name',
        'action',
        'description_text',
        'formula',
        'n_rows_selected',
        'is_filter',
    )
