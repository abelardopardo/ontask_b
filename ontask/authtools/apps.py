# -*- coding: utf-8 -*-
"""File defining the class with configuration operation"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthtoolsConfig(AppConfig):
    """Define app configuration."""
    name = 'authtools'
    verbose_name = _('Authtools')
