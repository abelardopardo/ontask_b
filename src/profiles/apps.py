# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.apps import AppConfig


class ProfileConfig(AppConfig):
    name = "profiles"
    verbose_name = 'User Profiles'

    def ready(self):
        pass
