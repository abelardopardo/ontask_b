# -*- coding: utf-8 -*-
"""
Implementation of visualizations using the Plotly JS libarry
"""
from __future__ import unicode_literals, print_function

import json

from dataops import pandas_db
from . import VisHandler


class PlotlyHandler(VisHandler):
    """
    Handler to produce Plotly visualizations.
    """

    head_scripts = ["https://cdn.plot.ly/plotly-latest.min.js"]

    html_skel = """<div id="{id}" style="{style}"></div>
        <script>
        Plotly.newPlot('{id}', {data}, {layout},
        {{displaylogo: false}});
        </script>"""

    def __init__(self, data, *args, **kwargs):

        super(PlotlyHandler, self).__init__(data, *args, **kwargs)

        self.format_dict = {
            'style': ''
        }

        self.layout = {'margin': {'l': 35, 'r': 35, 't': 35, 'b': 35}}

    def get_engine_scripts(self, current):
        """
        Return the HTML HEAD snippet including whatever <scripts> are required
        :return: String to include in HEAD
        """
        for script in self.head_scripts:
            if script not in current:
                current.append(script)
        return current

    def render(self):
        """
        Return the rendering in HTML fo this visualization
        :param args:
        :param kwargs:
        :return: String as HTML snippet
        """
        return self.html_content


class PlotlyBoxPlot(PlotlyHandler):
    """
    Create a boxplot with a given data frame column
    """

    def __init__(self, data, *args, **kwargs):

        super(PlotlyBoxPlot, self).__init__(data, *args, **kwargs)

        self.format_dict['id'] = 'boxplot-id'
        # Transfer the keys to the formatting dictionary
        for key, value in kwargs.pop('context', {}).items():
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
        if self.format_dict.get('individual_value', None) is not None:
            self.layout['annotations'] = [{
                'bgcolor': 'white',
                'x': 0,
                'y': self.format_dict['individual_value'],
                'ax': 0,
                'ay': 0,
                'xref': 'x',
                'yref': 'y',
                'text': self.format_dict.get('individual_text', 'Your value')
            }]

            # Get the two custom values from the given parameters.
            self.layout['annotations'][0]['y'] = \
                self.format_dict['individual_value']
            self.layout['annotations'][0]['text'] = \
                self.format_dict.get('individual_text', 'Your value')

            # Redefine the layout
            self.format_dict['layout'] = json.dumps(self.layout)

        self.format_dict['data'] = json.dumps(data)

        self.html_content = ''
        if self.format_dict.get('title', None):
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
    """
    Create a histogram
    """

    def __init__(self, data, *args, **kwargs):

        super(PlotlyColumnHistogram, self).__init__(data, *args, **kwargs)

        self.format_dict['id'] = 'histogram-id'

        self.layout.update({'autobinx': True,
                            'autobiny': True,
                            'bargap': 0.01,
                            'yaxis': {'title': 'Count'}})

        # Transfer the keys to the formatting dictionary
        for key, value in kwargs.pop('context', {}).items():
            self.format_dict[key] = value

        data = []
        for column in self.data.columns:
            column_dtype = \
                pandas_db.pandas_datatype_names[self.data[column].dtype.name]
        data_list = self.data[column].dropna().tolist()
        # Special case for bool and datetime. Turn into strings to be
        # treated as such
        if column_dtype == 'boolean' or column_dtype == 'datetime':
            data_list = [str(x) for x in data_list]

        data.append(
            {'x': data_list,
             'autobinx': True,
             'histnorm': 'count',
             'name': column,
             'type': 'histogram'}
        )

        self.format_dict['data'] = json.dumps(data)

        # If an individual value has been given, add the annotation and the
        # layout to the rendering.
        if self.format_dict.get('individual_value', None) is not None:
            ival = self.format_dict['individual_value']
        if column_dtype == 'boolean' or column_dtype == 'datetime':
            ival = str(ival)

        self.layout['annotations'] = [{
            'bgcolor': 'white',
            'x': ival,
            'ax': 0,
            'axref': 'pixel',
            'y': 0,
            'yref': 'paper',
            'yshift': 'bottom',
            'text': self.format_dict.get('individual_text', 'Your value')
        }]

        self.format_dict['layout'] = json.dumps(self.layout)

        self.html_content = ''
        if self.format_dict.get('title', None):
            self.html_content = self.format_dict['title']

        self.html_content += self.html_skel.format(**self.format_dict)

    def get_id(self):
        """
        Return the name of this handler
        :return: string with the name
        """
        return self.format_dict['id']


class PlotlyGauge(PlotlyHandler):
    """
    Create a gauge pointing to a value
    """

    # FIX FIX FIX
    format_dict = {
        'id': 'histogram-id',
        'data': "[{ y: [], type: 'histogram'}]",
        'layout': "{}"
    }

    # FIX FIX FIX
    layout = {
        'shapes': [{
            'type': 'path',
            'path': None,
            'fillcolor': '850000',
            'line': {'color': '850000'}
        }],
        'title': 'Gauge Speed 0 - 100',
        'height': 400,
        'width': 400,
        'xaxis': {
            'zeroline': False,
            'showticklabels': False,
            'showgrid': False,
            'range': [-1, 1]},
        'yaxis': {
            'zeroline': False,
            'showticklabels': False,
            'showgrid': False,
            'range': [-1, 1]}
    }

    def __init__(self, data, *args, **kwargs):
        # Transfer the keys to the formatting dictionary
        for key, value in kwargs.pop('context', {}).items():
            self.format_dict[key] = value

        super(PlotlyGauge, self).__init__(data, *args, **kwargs)

        data = []
        for column in self.data.columns:
            data.append(
                {'x': list(self.data[column].dropna()),
                 'autobinx': True,
                 'histnorm': 'count',
                 'name': column,
                 'type': 'histogram'}
            )
        self.format_dict['data'] = json.dumps(data)

        self.layout['bargap'] = 0.01
        self.layout['yaxis'] = {'title': 'Count'}

        self.format_dict['layout'] = json.dumps(self.layout)

        self.html_content = self.html_skel.format(**self.format_dict)

    def get_id(self):
        """
        Return the name of this handler
        :return: string with the name
        """
        return self.format_dict['id']
