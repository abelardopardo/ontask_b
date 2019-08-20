# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask.models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'name', 'workflow', 'payload')


admin.site.register(Log, LogAdmin)
