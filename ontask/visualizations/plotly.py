# -*- coding: utf-8 -*-
"""
Implementation of visualizations using the Plotly JS library
"""

from builtins import str
import json

from django.utils.translation import ugettext as _

from ontask.dataops.pandas import pandas_datatype_names
from ontask.visualizations import VisHandler


class PlotlyHandler(VisHandler):
    """Handler to produce Plotly visualizations."""

    head_scripts = [
        "//cdn.plot.ly/plotly-cartesian-latest.min.js"
    ]

    html_skel = """<div id="{id}" style="{style}"></div>
        <script>Plotly.newPlot('{id}', {data}, 
        {layout},
        {{displaylogo: false}});</script>"""

    def __init__(self, data, *args, **kwargs):

        super().__init__(data, *args, **kwargs)

        self.format_dict = {
            'style': 'width: 100%; height:100%;'
        }

        self.layout = {'autosize': True}

    @staticmethod
    def get_engine_scripts(current=None):
        """Return the scripts required for the HTML rendering.

        Return the HTML HEAD snippet including whatever <scripts> are required
        :return: String to include in HEAD
        """
        if current is None:
            return PlotlyHandler.head_scripts

        for script in PlotlyHandler.head_scripts:
            if script not in current:
                current.append(script)
        return current

    def render(self):
        """Return the rendering in HTML fo this visualization.

        :return: String as HTML snippet
        """
        return self.html_content


class PlotlyBoxPlot(PlotlyHandler):
    """Create a boxplot with a given data frame column."""

    def __init__(self, data, *args, **kwargs):

        super().__init__(data, *args, **kwargs)

        self.format_dict['id'] = 'boxplot-id'
        # Transfer the keys to the formatting dictionary
        for key, value in list(kwargs.pop('context', {}).items()):
            self.format_dict[key] = value

        data = []
        for column in self.data.columns:
            data.append(
                {'y': list(self.data[column].dropna()),
                 'name': column,
                 'type': 'box'}
            )

        # If an individual value has been given, add the annotation and the
        # layout to the rendering.
        if self.format_dict.get('individual_value') is not None:
            self.layout['annotations'] = [{
                'bgcolor': 'white',
                'x': 0,
                'y': self.format_dict['individual_value'],
                'ax': 0,
                'ay': 0,
                'xref': 'x',
                'yref': 'y',
                'text': self.format_dict.get(
                    'individual_text',
                    _('Your value'))
            }]

            # Get the two custom values from the given parameters.
            self.layout['annotations'][0]['y'] = \
                self.format_dict['individual_value']
            self.layout['annotations'][0]['text'] = \
                self.format_dict.get('individual_text', _('Your value'))

        # Redefine the layout
        self.format_dict['layout'] = json.dumps(self.layout)

        self.format_dict['data'] = json.dumps(data)

        self.html_content = ''
        if self.format_dict.get('title'):
            self.html_content = self.format_dict['title']

        self.html_content += self.html_skel.format(**self.format_dict)

        # If a title is given, place it in front of the widget

    def get_id(self):
        """
        Return the name of this handler
        :return: string with the name
        """
        return self.format_dict['id']


class PlotlyColumnHistogram(PlotlyHandler):
    """Create a histogram."""

    def _create_dictionaries(self, data, *args, **kwargs):
        self.format_dict['id'] = 'histogram-id'

        self.layout.update({
            'bargap': 0.01,
            'yaxis': {'title': 'Count'}})

        # Transfer the keys to the formatting dictionary
        for key, value in list(kwargs.pop('context', {}).items()):
            self.format_dict[key] = value

        data = []
        column = self.data.columns[0]
        column_dtype = pandas_datatype_names.get(self.data[column].dtype.name)
        data_list = self.data[column].dropna().tolist()
        # Special case for bool and datetime. Turn into strings to be
        # treated as such
        if (
            column_dtype == 'boolean' or column_dtype == 'datetime' or
            column_dtype == 'string'
        ):
            data_list = [str(x) for x in data_list]

        data.append(
            {'x': data_list,
             'histnorm': '',
             'name': column,
             'type': 'histogram'}
        )

        self.format_dict['data'] = data

        # If an individual value has been given, add the annotation and the
        # layout to the rendering.
        if self.format_dict.get('individual_value') is not None:
            ival = self.format_dict['individual_value']
            if column_dtype == 'boolean' or column_dtype == 'datetime':
                ival = str(ival)

            self.layout['annotations'] = [{
                'bgcolor': 'white',
                'x': ival,
                'ax': 0,
                'axref': 'pixel',
                'y': 0,
                'ay': -40,
                'yref': 'paper',
                'text': self.format_dict.get('individual_text', 'Your value')
            }]

        self.format_dict['layout'] = self.layout

        self.html_content = ''
        if self.format_dict.get('title'):
            self.html_content = self.format_dict['title']

        self.html_content += self.html_skel.format(**self.format_dict)

    def __init__(self, data, *args, **kwargs):
        """Create the new object."""
        super().__init__(data, *args, **kwargs)

        # Create the dictionaries with values
        self._create_dictionaries(data, *args, **kwargs)

        self.html_content = ''
        if self.format_dict.get('title'):
            self.html_content = self.format_dict['title']

        self.html_content += self.html_skel.format(
            style=self.format_dict['style'],
            id=self.format_dict['id'],
            data=json.dumps(self.format_dict['data']),
            layout=json.dumps(self.format_dict['layout']))

    def get_id(self):
        """Return the name of this handler.

        :return: string with the name
        """
        return self.format_dict['id']
