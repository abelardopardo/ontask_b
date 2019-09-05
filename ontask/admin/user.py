# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask.models import OnTaskUser


@admin.register(OnTaskUser)
class OnTaskUserAdmin(admin.ModelAdmin):
    pass
