# -*- coding: utf-8 -*-
"""
Implementation of visualizations using the Vega JS libarry
"""
from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod

class VisHandler:
    __metaclass__ = ABCMeta

    id = None

    @abstractmethod
    def __init__(self, data, *args, **kwargs):
        self.data = data
        super(VisHandler, self).__init__()

    @abstractmethod
    def get_engine_scripts(self, current):
        """
        Add to the given list the additional src attributes for the
        <script > elements to include in the HTML head
        :return: Nothing. Modify current list
        """
        pass

    @abstractmethod
    def get_id(self):
        """
        Return the name of this handler
        :return: string with the name
        """
        pass

    @abstractmethod
    def render(self):
        """
        Return the rendering in HTML fo this visualization
        :param args:
        :param kwargs:
        :return: String as HTML snippet
        """
        pass