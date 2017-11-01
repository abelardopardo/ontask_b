# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

import ontask

register = template.Library()


# settings value
@register.simple_tag
def ontask_version():
    return ontask.__version__
