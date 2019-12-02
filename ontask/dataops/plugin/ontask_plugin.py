# -*- coding: utf-8 -*-

"""Abstract class to use to inherit a plugin."""
from abc import ABCMeta
from builtins import object

from django.utils.translation import ugettext_lazy as _


class OnTaskPluginAbstract(object, metaclass=ABCMeta):
    """Abstract class to instantiate to create an OnTask plugin."""

    def __init__(self):
        """Initialize the object fields."""
        self.name = ''
        self.description_text = ''
        self.input_column_names = []
        self.output_column_names = []
        self.output_suffix = ''
        self.parameters = []

    def get_name(self):
        """Access the name."""
        return self.name

    def get_description_text(self):
        """Access the short description."""
        return self.description_text

    def get_long_description(self):
        """Access the long description."""
        return self.__doc__

    def get_is_model(self):
        """Access the is_mode field."""
        return isinstance(self, OnTaskModel)

    def get_input_column_names(self):
        """Access the list of input column names."""
        return self.input_column_names

    def get_output_column_names(self):
        """Access the list of output column names."""
        return self.output_column_names

    def get_output_suffix(self):
        """Access the output suffix."""
        return self.output_suffix

    def get_parameters(self):
        """Access the parameters."""
        return self.parameters

    def run(self, data_frame, parameters=dict):
        """Overwrite this method.

        Receives a data frame wih a number of columns
        between num_column_input_from and num_column_input_to and returns a
        pandas data frame structure that is appended to the existing one (
        after column renaming).

        :param data_frame: Input data for the plugin

        :param parameters: dictionary with the parameters

        :return: a Pandas data_frame to append to the existing one
        """
        raise Exception(_('This method should be implemented!'))


class OnTaskTransformation(OnTaskPluginAbstract):
    """Abstract class to instantiate to create an OnTask transformation."""


class OnTaskModel(OnTaskPluginAbstract):
    """Abstract class to instantiate to create an OnTask model."""
