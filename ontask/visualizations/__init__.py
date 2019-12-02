# -*- coding: utf-8 -*-
"""Implementation of visualizations using the Vega JS libarry."""
from abc import ABCMeta, abstractmethod
from builtins import object

from future.utils import with_metaclass


class VisHandler(with_metaclass(ABCMeta, object)):
    id = None

    head_scripts = []

    @abstractmethod
    def __init__(self, data, *args, **kwargs):
        self.data = data
        super().__init__()

    @staticmethod
    @abstractmethod
    def get_engine_scripts(current=None):
        """Add scripts to the given list.

        Add to the given list the additional src attributes for the
        <script > elements to include in the HTML head
        :return: Nothing. Modify current list
        """

    @abstractmethod
    def get_id(self):
        """Return the name of this handler.

        :return: string with the name
        """

    @abstractmethod
    def render(self):
        """Return the rendering in HTML fo this visualization.

        :return: String as HTML snippet
        """
