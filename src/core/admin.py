# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import OnTaskUser


class OnTaskUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(OnTaskUser, OnTaskUserAdmin)
