"""Classes for Athena connection admin."""
from django.contrib import admin

from ontask import models


@admin.register(models.AthenaConnection)
class AthenaConnectionAdmin(admin.ModelAdmin):
    """Admin for the Athena Connections."""

    list_display = (
        'id',
        'name',
        'description_text',
        'aws_access_key',
        'aws_secret_access_key',
        'aws_session_token',
        'aws_bucket_name',
        'aws_file_path',
        'aws_region_name',
        'table_name')

    search_fields = [
        'name',
        'description_text',
        'aws_access_key',
        'aws_secret_access_key',
        'aws_session_token',
        'aws_bucket_name',
        'aws_file_path',
        'aws_region_name',
        'table_name']
