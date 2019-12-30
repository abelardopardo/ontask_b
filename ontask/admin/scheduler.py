# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask import models


@admin.register(models.ScheduledOperation)
class ScheduledEmailActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'execute', 'status', 'action',
                    'last_executed_log')
