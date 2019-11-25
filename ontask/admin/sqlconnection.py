# -*- coding: utf-8 -*-

"""Classes for SQL connection admin."""

from django.contrib import admin

from ontask import models


@admin.register(models.SQLConnection)
class SQLConnectionAdmin(admin.ModelAdmin):
    """Admin for the SQL Connections."""

    list_display = (
        'id',
        'name',
        'description_text',
        'conn_type',
        'conn_driver',
        'db_user',
        'db_password',
        'db_host',
        'db_port',
        'db_name',
        'db_table')
