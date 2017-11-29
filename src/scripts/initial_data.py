# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

___doc___ = """
Script to create some initial data structures
"""


def run(*script_args):
    """
    Script to create some initial data structures.

    No arguments required.
    """

    # Create the instructor group if it does not exist
    if not Group.objects.filter(name='instructor').exists():
        group = Group(name='instructor')
        group.save()
    else:
        group = Group.objects.get(name='instructor')

