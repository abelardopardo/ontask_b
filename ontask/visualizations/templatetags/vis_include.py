"""functions to include the visualization code."""
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ontask.action import evaluate
from ontask.dataops import pandas
from ontask.templatetags.ontask_tags import ACTION_CONTEXT_VAR
from ontask.visualizations import plotly

register = template.Library()


def vis_html_content(context, column_name):
    """Create the HTML visualization code."""
    # Get the action
    action = context.get(ACTION_CONTEXT_VAR)
    if not action:
        raise Exception(_('Action object not found when processing tag'))
    workflow = action.workflow

    # Check if the column is correct
    if not workflow.columns.filter(name=column_name).exists():
        raise Exception(_('Column {0} does not exist').format(column_name))

    # Get the visualization number to generate unique IDs
    viz_number = context[evaluate.VIZ_NUMBER_CONTEXT_VAR]

    # Create the context for the visualization
    viz_ctx = {
        'style': 'width:400px; height:225px;',
        'id': 'viz_tag_{0}'.format(viz_number)
    }

    # If there is a column name in the context, insert it as individual value
    # If the template is simply being saved and rendered to detect syntax
    # errors, we may not have the data of an individual, so we have to relax
    # this restriction.
    ivalue = context.get(evaluate.TR_ITEM(column_name))
    if ivalue is not None:
        viz_ctx['individual_value'] = ivalue

    # Get the data from the data frame
    df = pandas.get_subframe(
        workflow.get_data_frame_table_name(),
        action.get_filter_formula(),
        [column_name])

    # Get the visualisation
    viz = plotly.PlotlyColumnHistogram(data=df, context=viz_ctx)

    prefix = ''
    if viz_number == 0:
        prefix = ''.join([
            '<script src="{0}"></script>'.format(x)
            for x in plotly.PlotlyColumnHistogram.get_engine_scripts()
        ])

    # Update viz number
    context[evaluate.VIZ_NUMBER_CONTEXT_VAR] = viz_number + 1

    # Return the rendering of the viz marked as safe
    return mark_safe(prefix + viz.render())


# Register the tag in the library.
register.simple_tag(func=vis_html_content,
                    takes_context=True,
                    name='visualization')
