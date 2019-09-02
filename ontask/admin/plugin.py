# -*- coding: utf-8 -*-

"""Classes for plugin admin."""

from django.contrib import admin

from ontask.models import Plugin


@admin.register(Plugin)
class PluginRegistryAdmin(admin.ModelAdmin):
    """Admin for the plugin registry."""

    list_display = (
        'id',
        'filename',
        'modified',
        'name',
        'description_text',
        'executed')

