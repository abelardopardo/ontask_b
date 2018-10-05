# -*- coding: utf-8 -*-
from django.forms.widgets import DateTimeBaseInput

class OnTaskDateTimeInput(DateTimeBaseInput):
    """
    <input type="{{ widget.type }}"
           name="{{ widget.name }}"
           {% if widget.value != None %}
             value="{{ widget.value|stringformat:'s' }}"
           {% endif %}
           {% for name, value in widget.attrs.items %}
             {% if value is not False %}
               {{ name }}
                 {% if value is not True %}
                 ="{{ value|stringformat:'s' }}"
                {% endif %}
             {% endif %}
         {% endfor %}
    """
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'ontask_datetime_widget.html'