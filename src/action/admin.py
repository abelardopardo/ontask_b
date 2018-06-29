# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import Action, Condition


class ActionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'workflow',
                    'name',
                    'description_text',
                    'created',
                    'modified',
                    '_content',
                    'serve_enabled'
                    )


class ConditionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'action',
                    'description_text',
                    'formula',
                    'n_rows_selected',
                    'is_filter')


admin.site.register(Action, ActionAdmin)
admin.site.register(Condition, ConditionAdmin)
