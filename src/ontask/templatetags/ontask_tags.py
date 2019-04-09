# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html
from django.contrib.staticfiles.templatetags.staticfiles import static

import ontask

register = template.Library()

jquery = \
    """<script src="//code.jquery.com/jquery-3.3.1.min.js"></script>
       <script src="//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.0/jquery.validate.min.js"></script>
       <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.0/additional-methods.min.js"></script>"""

#
# Bootstrap
#
bootstrap_css = \
    """<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <link href="//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">"""

bootstrap_js = \
    """<script src="//cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
<script src="//stackpath.bootstrapcdn.com/
bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>"""

#
# Datatables
#
datatables_bootstrap_css = \
    """<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/v/bs4/dt-1.10.19/cr-1.5.0/r-2.2.2/fc-3.2.5/rr-1.2.4/sc-1.5.0/datatables.min.css"/>"""

datatables_jquery_js = \
    """<script src="//cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>"""

datatables_bootstrap_js = \
    """<script type="text/javascript" src="//cdn.datatables.net/v/bs4/dt-1.10.19/cr-1.5.0/r-2.2.2/fc-3.2.5/rr-1.2.4/sc-1.5.0/datatables.min.js"></script>"""

#
# Datetimepicker:
#
datetimepicker_css = \
    """<link href="//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/css/bootstrap-datetimepicker.css" type="text/css" media="all" rel="stylesheet">
    <link href="{0}" type="text/css" media="all" rel="stylesheet">""".format(
        static('bootstrap_datepicker_plus/css/datepicker-widget.css')
    )

datetimepicker_js = \
    '<script type="text/javascript" src="{0}"></script>'.format(
      static('site/js/moment-with-locales.js')
    ) + """<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/js/bootstrap-datetimepicker.min.js"></script>
<script type="text/javascript" src="{0}"></script>""".format(
        static('bootstrap_datepicker_plus/js/datepicker-widget.js')
    )

#
# Auxiliary
#
shim_and_respond = \
    """<!--[if lt IE 9]>
  <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
  <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
<![endif]-->"""

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
