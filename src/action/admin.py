# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import Action, Condition


class ActionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'workflow',
                    'description_text',
                    'created',
                    'n_selected_rows',
                    'content',
                    'serve_enabled'
                    )


class ConditionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'action',
                    'description_text',
                    'formula',
                    'is_filter')


admin.site.register(Action, ActionAdmin)
admin.site.register(Condition, ConditionAdmin)
