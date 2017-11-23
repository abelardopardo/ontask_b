# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf import settings 

def conf_to_context(request):
    """
    Function to include certain values of settins in the request context 
    to make it available to any view.
    :param request: HTTP request requiring a context
    :return: Dictionary with available values
    """
    return {'ONTASK_HELP_URL': settings.ONTASK_HELP_URL}

