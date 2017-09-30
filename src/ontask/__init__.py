# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib.auth.decorators import login_required

# Variable name regexp
# identifier ::=  (letter|"_") (letter | digit | "_")*
# letter     ::=  lowercase | uppercase
# lowercase  ::=  "a"..."z"
# uppercase  ::=  "A"..."Z"
# digit      ::=  "0"..."9"
var_names_re = re.compile('^[a-zA-Z_]\w*$')

# Decorators to guarantee that functions are executed by login instructors
decorators = [login_required, ]


# Function to check if a user belongs to a group
def is_instructor(user):
    return user.groups.filter(name='instructor').exists()


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


# def load_module(module_dir):
#
#     """
#     :param module_dir: Full path to a python module to load."""
#
#     if not os.path.isdir(module_dir):
#         raise Exception('%s must be a directory containing a python module.' %
#                         module_dir)
#
#     # Extract the path to add to system path and make the load work
#     (module_dir, module_suffix) = os.path.split(os.path.abspath(module_dir))
#
#     # Insert dirname in the path to load modules
#     if module_dir not in sys.path:
#         sys.path.insert(0, module_dir)
#
#     # Load the given module
#     try:
#         ctx_handler = __import__(module_suffix)
#     except Exception as e:
#         # Display error message
#         print(e)
#         print('Unable to import', module_dir, '. Terminating.')
#         sys.exit(1)
#
#     class_name = HandlerBasic.expected_class_name
#     try:
#         handler_class = getattr(ctx_handler, class_name)
#     except AttributeError:
#         print('No class with name', class_name, 'in module.')
#         sys.exit(1)
#
#     return handler_class()
