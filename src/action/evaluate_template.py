# -*- coding: utf-8 -*-

"""Manipulate template text within OnTask and evaluat it s content."""

import re
import string
from builtins import map, str
from typing import Mapping

from django.template import Context, Template
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from action.models import Action, var_use_res

# Variable name to store the workflow ID in the context used to render a
# template
action_context_var = 'ONTASK_ACTION_CONTEXT_VARIABLE___'
viz_number_context_var = 'ONTASK_VIZ_NUMBER_CONTEXT_VARIABLE___'

# Regular expression and replacements replace whitespace surrounding condition
# markup
white_space_res = [
    (re.compile(r'\n[ \t\r\f\v]*{% if '), '{% if '),
    (re.compile(r'{% endif %}[ \t\r\f\v]*\n'), '{% endif %}'),
]


def make_xlat(*args, **kwds):
    """Apply multiple character substitutions.

    Auxiliary function to define a translator that applies multiple character
    substitutions at once.

    Taken from "Python Cookbook, 2nd Edition by David Ascher, Anna Ravenscroft,
    Alex Martelli", Section 1.18

    :param args: Dictionary
    :param kwds:
    :return: A function that uses the given dictionary to apply multiple
    changes to a string
    """
    adict = dict(*args, **kwds)
    rx = re.compile(r'|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]

    def xlat(text: str) -> str:
        return rx.sub(one_xlat, text)

    return xlat


# Dictionary to translate non alphanumeric symbols into alphanumeric pairs
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
# abcdefghijklmnopqrstuvwxyzABCDEFG
tr_item = make_xlat(
    {
        '!': '_a',
        '"': '_b',
        '#': '_c',
        '$': '_d',
        '%': '_e',
        '&': '_f',
        "'": '_g',
        '(': '_h',
        ')': '_i',
        '*': '_j',
        '+': '_k',
        ',': '_l',
        '-': '_m',
        '.': '_n',
        '/': '_o',
        ':': '_p',
        ';': '_q',
        '<': '_r',
        '=': '_s',
        '>': '_t',
        '?': '_u',
        '@': '_v',
        '[': '_w',
        '\\': '_x',
        ']': '_y',
        '^': '_z',
        '_': '_0',
        '`': '_1',
        '{': '_2',
        '|': '_3',
        '}': '_4',
        '~': '_5',
        ' ': '_6',
    },
)


def translate(varname: str) -> str:
    """Apply several translations to the value of a variable.

    Function that given a string representing a variable name applies a
    translation to each of the non alphanumeric characters in that name.
    Additionally, it needs to guarantee that the name starts with a letter
    (not a digit), and it detects and fixes this condition by introducing a
    prefix.

    :param varname: Variable name
    :return: New variable name starting with a letter followed only by
             letter, digit or _
    """
    # If the variable name is surrounded by quotes, we leave it untouched!
    # because it represents a literal
    if varname.startswith("'") and varname.endswith("'"):
        return varname

    if varname.startswith('"') and varname.endswith('"'):
        return varname

    # If the variable name starts with a non-letter or the prefix used to
    # force letter start, add a prefix.
    if not varname[0] in string.ascii_letters or varname.startswith('OT_'):
        varname = 'OT_' + varname

    # Return the new variable name surrounded by the detected marks.
    return tr_item(varname)


def clean_whitespace(template_text: str) -> str:
    """Remove whitespace before and after conditionals.

    Function to detect new lines before and after the conditional template
    macros and removes it.

    :param template_text: Initial template text
    :return: Modified template text
    """
    # Loop over the regular expressions and apply them to the given text
    for rexp, replace in white_space_res:
        template_text = rexp.sub(replace, template_text)

    return template_text


def render_template(
    template_text: str,
    context_dict: Mapping,
    action: Action = None,
) -> str:
    """Render a template using a given context.

    Given a template text and a context, performs the rendering of the
    template using the django template mechanism but with an additional
    pre-processing to bypass the restriction imposed by Jinja/Django that the
    variable names must start with a letter followed by a letter, number or _.

    In OnTask, the variable names are: column names, attribute names,
    or condition names. It is too restrictive to propagate the restrictions
    imposed by Jinja variables all the way to these three components. To
    hide this from the users, there is a preliminary step in which those
    variables in the template and keys in the context that do not comply with
    the syntax restriction are renamed to compliant names.

    The problem:
    We are giving two objects: a string containing a template with two markup
    structures denoting the use of variables, and a dictionary that matches
    variables to values.

    The processing of the template is done through Django template engine
    (itself based in Jinja). The syntax for the variables appearing in the
    template is highly restrictive. It only allows names starting with a
    letter followed by letter, number or '_'. No other printable symbol is
    allowed. We want to relax this last restriction.

    The solution:
    1) Parse the template and detect the use of all variables.

    2) For each variable use, transform its name into a name that is legal
       for Jinja (starts with letter followed by letter, number or '_' *)

       The transformation is based on:
       - Every non-letter or number is replaced by '_' followed by a
         letter/number as specified by the dictionary below.

       - If the original variable does not start by a letter, insert a prefix.

    3) Apply the same transformation for the keys in the given dictionary

    4) Execute the new template with the new dictionary and return the result.

    :param template_text: Text in the template to be rendered
    :param context_dict: Dictionary used by Jinja to evaluate the template
    :param action: Action object to insert in the context in case it is
    needed by any other custom template.
    :return: The rendered template
    """
    # Steps 1 and 2. Apply the tranlation process to all variables that
    # appear in the the template text
    new_template_text = template_text
    for rexpr in var_use_res:
        new_template_text = rexpr.sub(
            lambda match: match.group('mup_pre')
                          + translate(match.group('vname'))
                          + match.group('mup_post'),
            new_template_text)

    # Step 2.2 Remove pre-and post white space from the {% if %} and
    # {% endif %} conditions (to reduce white space when using non HTML
    # content.
    new_template_text = clean_whitespace(new_template_text)

    # Step 3. Apply the translation process to the context keys
    new_context = {
        translate(escape(key)): str_val
        for key, str_val in list(context_dict.items())
    }

    # If the number of elements in the two dictionaries is different, we have
    #  a case of collision in the translation. Need to stop immediately.
    assert len(context_dict) == len(new_context)

    if action_context_var in new_context:
        raise Exception(_('Name {0} is reserved.').format(action_context_var))
    new_context[action_context_var] = action

    if viz_number_context_var in new_context:
        raise Exception(_('Name {0} is reserved.').format(
            viz_number_context_var,
        ))
    new_context[viz_number_context_var] = 0

    # Step 4. Return the redering of the new elements
    return Template(new_template_text).render(Context(new_context))


def run(*unused):
    """Script for testing purposes.

    :param script_args:
    :return: Nothing
    """
    # template = """
    # hi --{{ one }}--
    # --{% if var1 %}var1{% endif %}--
    # --{% if var2 %}var2{% endif %}--
    # --{% if !"# %}var3{% endif %}--
    # --{% if $%& %}var4{% endif %}--
    # --{% if '() %}var5{% endif %}--
    # --{{ +,- }}--
    # --{{ ./: }}--
    # --{{ ;<= }}--
    # --{{ >?@ }}--
    # --{{ [\] }}--
    # --{{ ^_` }}--
    # --{{ {|}~ }}--
    # --{{ this one has spaces }}--
    # --{{ OT_ The prefix }}--
    # --{{ OT_The prefix 2 }}--
    # """

    template = (
        '<p>Hi&nbsp;{{ !"#$%&amp;()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~ }}</p>'
    )

    context = {
        '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~': 'Carmelo Coton',
    }

    print((escape(list(context.items())[0][0])))
    print((render_template(template, context)))
