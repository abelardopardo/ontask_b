# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import re

__version__ = 'B.2.1.1'

# Variable name regexp
# identifier ::=  (letter|"_") (letter | digit | "_")*
# letter     ::=  lowercase | uppercase
# lowercase  ::=  "a"..."z"
# uppercase  ::=  "A"..."Z"
# digit      ::=  "0"..."9"
var_names_re = re.compile('^[a-zA-Z]\w*$')


def is_legal_var_name(val):
    """
    Function that returns if the parameter is a legal python variable
    :param val: variable name to chec,
    :return: Boolean stating if val is a legal python name
    """
    return var_names_re.match(val)

def is_legal_column_name(val):
    """
    Function to check if a string is a valid column name

    These are the characters that have been found to be problematic with
    column names and the responsibles for these anomalies:

    - ()%: In column names. pandas.to_sql. Breaks down because they are used in
       the internal translation into SQL queries.

    - \. DataTables displaying the column names in the "Tables" screen.

    - " Provokes a db error when updating the data base (probably fixable)

    - ' String delimiter, python messes around with it and it is too complex to
        handle.

    :param val: String with the column name
    :return: String with a message suggesting changes, or None if string correct

    """

    if '(' in val or ')' in val:
        return 'Replace () for [] in the name.'

    if '%' in val:
        return 'The symbol % cannot be used as column name.'

    if '.' in val:
        return 'The dot cannot be used in the column name.'

    if '\\' in val:
        return 'The symbol "\\" cannot be used in the column name.'

    if '"' in val:
        return 'The symbol " cannot be used in the column name.'

    if "'" in val:
        return "The symbol ' cannot be used in the column name."
    return None


def clean_column_name(val):
    """
    Function to transform column names and remove characters that are
    problematic with pandas <-> SQL (such as parenthesis) and others.
    :param val:
    :return: New val
    """

    return val.replace('(', '[').replace(')', ']').replace('%', 'PCT')


class OntaskException(Exception):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return repr(self.value)


