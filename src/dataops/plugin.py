# -*- coding: utf-8 -*-


from builtins import object
from abc import ABCMeta
from django.utils.translation import ugettext_lazy as _
from future.utils import with_metaclass

class_name = 'OntaskPlugin'


class OntaskPluginAbstract(with_metaclass(ABCMeta, object)):
    """
    Abstract class to instantiate to create an OnTask plugin.
    """

    name = ''

    description_txt = ''

    num_column_input_from = 0

    num_column_input_to = 0

    def __init__(self):
        pass

    def get_name(self):
        return self.name

    def get_description_txt(self):
        return self.description_txt

    def get_num_column_input_from(self):
        return self.num_column_input_from

    def get_num_column_input_to(self):
        return self.num_column_input_to

    def run(self, data_frame):
        """
        Method to ovewrite. Receives a data frame wih a number of columns
         between num_column_input_from and num_column_input_to and returns
         a pandas data frame structure that is appended to the existing
         one (after column renaming).

        :param data_frame: Input data for the plugin
        :return: a Pandas data_frame to append to the existing one
        """

        raise Exception(_('This method should be implemented!'))
