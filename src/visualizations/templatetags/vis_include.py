# -*- coding: utf-8 -*-

"""functions to include the visualization code."""

from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from action.evaluate import action_context_var, tr_item, viz_number_context_var
from dataops.pandas import get_subframe
from visualizations.plotly import PlotlyColumnHistogram

register = template.Library()


def vis_html_content(context, column_name):
    """Create the HTML visualization code."""
    # Get the action
    action = context.get(action_context_var)
    if not action:
        raise Exception(_('Action object not found when processing tag'))
    workflow = action.workflow

    # Check if the column is correct
    if not workflow.columns.filter(name=column_name).exists():
        raise Exception(_('Column {0} does not exist').format(column_name))

    # Get the visualization number to generate unique IDs
    viz_number = context[viz_number_context_var]

    # Create the context for the visualization
    viz_ctx = {
        'style': 'width:400px; height:225px;',
        'id': 'viz_tag_{0}'.format(viz_number)
    }

    # If there is a column name in the context, insert it as individual value
    # If the template is simply being saved and rendered to detect syntax
    # errors, we may not have the data of an individual, so we have to relax
    # this restriction.
    ivalue = context.get(tr_item(column_name))
    if ivalue is not None:
        viz_ctx['individual_value'] = ivalue

    # Get the data from the data frame
    df = get_subframe(
        workflow.get_data_frame_table_name(),
        action.get_filter_formula(),
        [column_name])

    # Get the visualisation
    viz = PlotlyColumnHistogram(data=df, context=viz_ctx)

    prefix = ''
    if viz_number == 0:
        prefix = ''.join([
            '<script src="{0}"></script>'.format(x)
            for x in PlotlyColumnHistogram.get_engine_scripts()
        ])

    # Update viz number
    context[viz_number_context_var] = viz_number + 1

    # Return the rendering of the viz marked as safe
    return mark_safe(prefix + viz.render())


# Register the tag in the library.
register.simple_tag(func=vis_html_content,
                    takes_context=True,
                    name='visualization')
