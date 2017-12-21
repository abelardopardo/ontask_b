# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import re

__version__ = 'B.2.1.1'

def is_legal_name(val):
    """
    Function to check if a string is a valid column name, attribute name or
    condition name.

    These are the characters that have been found to be problematic with
    these names and the responsibles for these anomalies:

    - " Provokes a db error when handling the templates due to the encoding
      produced by the text editor.

    - ' String delimiter, python messes around with it and it is too complex to
        handle all possible cases and translations.

    In principle, arbitrary combinations of the following symbols should be
    handle by OnTask::

      !#$%&()*+,-./:;<=>?@[\]^_`{|}~

    :param val: String with the column name
    :return: String with a message suggesting changes, or None if string correct

    """

    if "'" in val:
        return "The symbol ' cannot be used in the column name."

    if '"' in val:
        return 'The symbol " cannot be used in the column name.'

    return None

def fix_pctg_in_name(val):
    return val.replace('%', '%%')


class OntaskException(Exception):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return repr(self.value)


