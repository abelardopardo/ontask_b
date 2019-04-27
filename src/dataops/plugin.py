# -*- coding: utf-8 -*-


from builtins import object
from abc import ABCMeta
from django.utils.translation import ugettext_lazy as _
from future.utils import with_metaclass

class_name = 'OnTaskPlugin'


class OnTaskPluginAbstract(with_metaclass(ABCMeta, object)):
    """
    Abstract class to instantiate to create an OnTask plugin.
    """

    name = ''

    description_txt = ''

    is_model = False

    input_column_names = []

    output_column_names = []

    output_suffix = ''

    parameters = {}

    def __init__(self):
        self.name = ''
        self.description_txt = ''
        self.input_column_names = []
        self.output_column_names = []
        self.output_suffix = ''
        self.paramters = {}

    def get_name(self):
        return self.name

    def get_description_txt(self):
        return self.description_txt

    def get_long_description(self):
        return self.__doc__

    def get_is_model(self):
        return self.is_model

    def get_input_column_names(self):
        return self.input_column_names

    def get_output_column_names(self):
        return self.output_column_names

    def get_output_suffix(self):
        return self.output_suffix

    def get_parameters(self):
        return self.parameters

    def run(self, data_frame, parameters=dict):
        """
        Method to ovewrite. Receives a data frame wih a number of columns
        between num_column_input_from and num_column_input_to and returns a
        pandas data frame structure that is appended to the existing one (
        after column renaming).

        :param data_frame: Input data for the plugin
        :param parameters: dictionary with the parameters
        :return: a Pandas data_frame to append to the existing one
        """

        raise Exception(_('This method should be implemented!'))
