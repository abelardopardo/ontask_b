# -*- coding: utf-8 -*-

"""Admin definitions."""

from django.contrib import admin

from ontask.action.models import Action, Condition


class ActionAdmin(admin.ModelAdmin):
    """Define Action Admin."""

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


admin.site.register(Action, ActionAdmin)
admin.site.register(Condition, ConditionAdmin)
