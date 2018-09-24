# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

import ontask

register = template.Library()


# Tag to get ontask_version
@register.simple_tag
def ontask_version():
    return ontask.__version__


@register.simple_tag
def otv():
    """
    Function to return a URL query parameter with the ontask version to force
    refresh of javascript URLs
    :return: The query param to add to the end of a URL
    """
    return '?v=' + ontask.__version__
