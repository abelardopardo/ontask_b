# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import re

__version__ = 'B.1.0.3'

# Variable name regexp
# identifier ::=  (letter|"_") (letter | digit | "_")*
# letter     ::=  lowercase | uppercase
# lowercase  ::=  "a"..."z"
# uppercase  ::=  "A"..."Z"
# digit      ::=  "0"..."9"
var_names_re = re.compile('^[a-zA-Z]\w*$')


def slugify(val):
    """
    Replace all spaces to underscores to facilitate column name manipulation
    :param val: String
    :return: another string with ' ' replaced by '_'
    """
    return val.strip().replace(' ', '_')


def is_legal_var_name(val):
    """
    Function that returns if the parameter is a legal python variable
    :param val: variable name to chec,
    :return: Boolean stating if val is a legal python name
    """
    return var_names_re.match(val)


def are_legal_vars(lvar):
    """
    Function to check if a set of variable names are all legal
    :param lvar: List of variable names
    :return: Boolean stating if all of them are legal variable names
    """
    return all([var_names_re.match(z) for z in lvar])


def find_ilegal_var(lvar):
    """
    Function to find an ilegal variable name in a list
    :param lvar: List of variable names
    :return: A pair with the first ilegal variable name and its index or None
    """
    for idx, var in enumerate(lvar):
        if not var_names_re.match(var):
            # found one that does not match
            return idx, var

    # All of them match
    return None


class OntaskException(Exception):

        def __init__(self, msg, value):
            self.msg = msg
            self.value = value

        def __str__(self):
            return repr(self.value)
