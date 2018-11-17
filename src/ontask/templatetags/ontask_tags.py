# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html

import ontask

register = template.Library()

jquery = """<script src="//code.jquery.com/jquery-3.3.1.min.js"></script>"""

bootstrap_css = \
    """<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">"""
bootstrap_js = \
    """<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>"""

shim_and_respond = \
    """<!--[if lt IE 9]>
  <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
  <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
<![endif]-->"""

datatables_bootstrap_css = \
    """<link rel="stylesheet" href="//cdn.datatables.net/1.10.19/css/dataTables.bootstrap.min.css">"""

datatables_jquery_js = \
    """<script src="//cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>"""

datatables_bootstrap_js = \
    """<script src="//cdn.datatables.net/1.10.19/js/dataTables.bootstrap.min.js"></script>"""

datetimepicker_css = \
    """<link href="//cdnjs.cloudflare.com/ajax/libs/eonasdan-bootstrap-datetimepicker/4.17.47/css/bootstrap-datetimepicker.min.css" rel="stylesheet">"""

datetimepicker_js = \
    """<script src="//cdn.bootcss.com/moment.js/2.17.1/moment-with-locales.min.js"></script>
       <script src="//cdnjs.cloudflare.com/ajax/libs/eonasdan-bootstrap-datetimepicker/4.17.47/js/bootstrap-datetimepicker.min.js"></script>"""

# Tag to get ontask_version
@register.simple_tag
def ontask_version():
    return ontask.__version__

@register.filter
def country(value):
    return value[0:value.find("-")]

@register.simple_tag
def ontask_jquery():
    return format_html(jquery)


@register.simple_tag
def ontask_bootstrap_css():
    return format_html(bootstrap_css)


@register.simple_tag
def ontask_bootstrap_js():
    return format_html(bootstrap_js)


@register.simple_tag
def ontask_shim_respond():
    return format_html(shim_and_respond)


@register.simple_tag
def ontask_datatables_jquery_js():
    return format_html(datatables_jquery_js)


@register.simple_tag
def ontask_datatables_bootstrap_css():
    return format_html(datatables_bootstrap_css)


@register.simple_tag
def ontask_datatables_bootstrap_js():
    return format_html(datatables_bootstrap_js)


@register.simple_tag
def ontask_datetimepicker_css():
    return format_html(datetimepicker_css)


@register.simple_tag
def ontask_datetimepicker_js():
    return format_html(datetimepicker_js)
