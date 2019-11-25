# -*- coding: utf-8 -*-

"""Classes for plugin admin."""

from django.contrib import admin

from ontask import models


@admin.register(models.Plugin)
class PluginRegistryAdmin(admin.ModelAdmin):
    """Admin for the plugin registry."""

    list_display = (
        'id',
        'filename',
        'modified',
        'name',
        'description_text',
        'executed')
