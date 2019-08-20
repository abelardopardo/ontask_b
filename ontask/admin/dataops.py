# -*- coding: utf-8 -*-

"""Classes for admin application."""

from django.contrib import admin

from ontask.models import Plugin, SQLConnection


class PluginRegistryAdmin(admin.ModelAdmin):
    """Admin for the plugin registry."""

    list_display = (
        'id',
        'filename',
        'modified',
        'name',
        'description_txt',
        'executed')


class SQLConnectionAdmin(admin.ModelAdmin):
    """Admin for the SQL Connections."""

    list_display = (
        'id',
        'name',
        'description_txt',
        'conn_type',
        'conn_driver',
        'db_user',
        'db_password',
        'db_host',
        'db_port',
        'db_name',
        'db_table')


admin.site.register(Plugin, PluginRegistryAdmin)
admin.site.register(SQLConnection, SQLConnectionAdmin)
