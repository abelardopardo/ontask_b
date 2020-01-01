# -*- coding: utf-8 -*-

"""Tags to include URLS and other auxiliary HTML resources."""
import json

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import ontask
from ontask import models
from ontask.action import evaluate
from ontask.dataops import sql

register = template.Library()


# Tag to get ontask_version
@register.simple_tag
def ontask_version() -> str:
    """Return ontask version."""
    return ontask.__version__


@register.filter
def country(country_code) -> str:
    """Extract the country from the given variable."""
    return ontask.get_country_code(country_code)


@register.simple_tag
def ontask_jquery() -> str:
    """Provide the JQuery URL."""
    return format_html(
        '<script src="//code.jquery.com/jquery-3.4.1.min.js"></script>'
        + '<script src="//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19'
          '.0/jquery.validate.min.js"></script>'
        + '<script src="//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19'
          '.0/additional-methods.min.js"></script>')


@register.simple_tag
def ontask_jqcron_js() -> str:
    """Provide the jqCron jquery files"""
    return format_html(
        '<script src="{0}js/jqCron/jqCron.js"></script>'.format(
            settings.STATIC_URL)
        + '<script src="{0}js/jqCron/jqCron.{1}.js"></script>'.format(
            settings.STATIC_URL,
            ontask.get_country_code(settings.LANGUAGE_CODE)))


@register.simple_tag
def ontask_jqcron_css() -> str:
    """Provide the jqCron CSS files"""
    return format_html(
        '<link rel="stylesheet" href="{0}css/jqCron/jqCron.css">'.format(
            settings.STATIC_URL))


@register.simple_tag
def ontask_bootstrap_css() -> str:
    """Provide bootstrap CSS."""
    return format_html(
        '<link rel="stylesheet" '
        'href="//stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min'
        '.css" integrity="sha384-MCw98'
        '/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" '
        'crossorigin="anonymous">'
        + '<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font'
          '-awesome.min.css" rel="stylesheet">')


@register.simple_tag
def ontask_bootstrap_js() -> str:
    """Provide the bootstrap JS."""
    return format_html(
        '<script src="//cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd'
        '/popper.min.js" '
        'integrity="sha384-ZMP7rVo3mIykV+2'
        '+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" '
        'crossorigin="anonymous"></script>'
        + '<script src="//stackpath.bootstrapcdn.com/bootstrap/4.1.3/js'
          '/bootstrap.min.js" '
          'integrity="sha384-ChfqqxuZUCnJSK3'
          '+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" '
          'crossorigin="anonymous"></script>')


@register.simple_tag
def ontask_datatables_jquery_js() -> str:
    """Provide the datatables JQuery JS URL."""
    return format_html(
        '<script src="//cdn.datatables.net/1.10.18/js/jquery.dataTables.min'
        '.js"></script>')


@register.simple_tag
def ontask_datatables_bootstrap_css() -> str:
    """Provide the datatables bootstrap CSS URL."""
    return format_html(
        '<link rel="stylesheet" type="text/css" '
        'href="//cdn.datatables.net/v/bs4/dt-1.10.18/cr-1.5.0/r-2.2.2/fc-3.2'
        '.5/rr-1.2.4/sc-1.5.0/datatables.min.css"/>')


@register.simple_tag
def ontask_datatables_bootstrap_js() -> str:
    """Provide the datatables bootstrap JS URL."""
    return format_html(
        '<script type="text/javascript" '
        'src="//cdn.datatables.net/v/bs4/dt-1.10.18/cr-1.5.0/r-2.2.2/fc-3.2.5'
        '/rr-1.2.4/sc-1.5.0/datatables.min.js"></script>')


@register.simple_tag
def ontask_datetimepicker_css() -> str:
    """Provide the datetime picker CSS URL."""
    return format_html(
        ('<link href="//cdnjs.cloudflare.com/ajax/libs/bootstrap'
         + '-datetimepicker/4.17.47/css/bootstrap-datetimepicker.css" '
         + 'type="text/css" media="all" rel="stylesheet"><link href="{'
         + '0}bootstrap_datepicker_plus/css/datepicker-widget.css" '
         + 'type="text/css" media="all" rel="stylesheet">').format(
            settings.STATIC_URL))


@register.simple_tag
def ontask_datetimepicker_js() -> str:
    """Provide the datetime picker JS URL."""
    return format_html(
        ('<script type="text/javascript" src="{'
         + '0}js/moment-with-locales.js"></script>').format(
            settings.STATIC_URL)
        + ('<script type="text/javascript" '
           + 'src="//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4'
           + '.17.47/js/bootstrap-datetimepicker.min.js"></script><script '
           + 'type="text/javascript" src="{'
           + '0}bootstrap_datepicker_plus/js/datepicker-widget.js"></script'
           + '>').format(settings.STATIC_URL))


@register.simple_tag(takes_context=True)
def ot_insert_column_list(context, column_name) -> str:
    """Insert in the text a column list."""
    action = context['ONTASK_ACTION_CONTEXT_VARIABLE___']
    column_values = [
        str(citem[0]) for citem in sql.get_rows(
            action.workflow.get_data_frame_table_name(),
            column_names=[column_name],
            filter_formula=action.get_filter_formula())]
    if action.action_type == models.Action.JSON_LIST:
        return mark_safe(json.dumps(column_values))

    return ', '.join(column_values)


@register.simple_tag(takes_context=True)
def ot_insert_rubric_feedback(context) -> str:
    """Insert in the text the rubric feedback."""
    return render_to_string(
        'action/includes/partial_rubric_message.html',
        context={
            'text_sources': evaluate.render_rubric_criteria(
                context['ONTASK_ACTION_CONTEXT_VARIABLE___'], context)})


@register.simple_tag
def ontask_shim_respond() -> str:
    """Provide additional JS URLs."""
    return format_html(
        '<!--[if lt IE 9]><script '
        'src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script'
        '><script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js'
        '"></script><![endif]-->')
