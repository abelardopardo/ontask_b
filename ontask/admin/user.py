# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask import models


@admin.register(models.OnTaskUser)
class OnTaskUserAdmin(admin.ModelAdmin):
    """Admin class for OnTask User objects."""

    search_fields = ['user__email']
