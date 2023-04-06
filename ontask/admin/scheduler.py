
from django.contrib import admin

from ontask import models


@admin.register(models.ScheduledOperation)
class ScheduledOperationAdmin(admin.ModelAdmin):
    """Admin class for Scheduled actions"""

    date_hierarchy = 'created'

    list_display = (
        'user',
        'created',
        'execute',
        'status',
        'action',
        'last_executed_log')

    search_fields = [
        'user',
        'status',
        'action',
        'last_executed_log']
