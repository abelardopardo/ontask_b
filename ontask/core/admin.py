# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask.core.models import OnTaskUser


class OnTaskUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(OnTaskUser, OnTaskUserAdmin)
