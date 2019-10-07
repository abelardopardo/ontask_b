# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask.models import ScheduledOperation


@admin.register(ScheduledOperation)
class ScheduledEmailActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'execute',
                    'status', 'action', 'item_column', 'last_executed_log')
