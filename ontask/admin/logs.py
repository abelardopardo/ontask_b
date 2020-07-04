# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask import models


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'

    list_display = ('id', 'user', 'created', 'name', 'workflow', 'payload')
    search_fields = ['id', 'user', 'created', 'name', 'workflow', 'payload']
