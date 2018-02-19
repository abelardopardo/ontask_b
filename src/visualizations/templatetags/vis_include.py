# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html

from workflow.models import Column
from workflow.ops import get_workflow

register = template.Library()

def vis_html_content(context, column_name, vtype=None):
    # Get the workflow
    workflow = get_workflow(context['request'])
    if not workflow:
        raise Exception('Workflow object not found in request')

    # Check if the column is correct
    if not Column.objects.filter(workflow=workflow, name=column_name).exists():
        raise Exception('Column {0} does not exist'.format(column_name))

    if vtype not in [None, 'histogram', 'boxplot']:
        raise Exception('Visualization type must be histogram or boxplot')

    # TO BE DESIGNED HOW THE MACRO IS THEN EVALUATED WITH THE RIGHT PERSONAL
    # DATA. NO IDEA HOW TO DO IT SO FAR.
    return format_html('<p>{0} {1}</p>'.format(column_name, vtype))

# Register the tag in the library.
register.simple_tag(func=vis_html_content,
                    takes_context=True,
                    name = 'visualization')