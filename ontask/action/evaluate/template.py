"""Manipulate template text within OnTask and evaluate its content."""
import re
import shlex
import string
from typing import Callable, Dict, List, Mapping

from django.template import Context, Template
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from ontask import models
# Variable name to store the action ID in the context used to render a
# template
from ontask.templatetags import ACTION_CONTEXT_VAR

VIZ_NUMBER_CONTEXT_VAR = 'ONTASK_VIZ_NUMBER_CONTEXT_VARIABLE___'

# Regular expression and replacements replace whitespace surrounding condition
# markup
WHITE_SPACE_RES = [
    (re.compile(r'\n[ \t\r\f\v]*{% if '), '{% if '),
    (re.compile(r'{% endif %}[ \t\r\f\v]*\n'), '{% endif %}'),
]

# Template prelude to load the ontask_tags
_ONTASK_TEMPLATE_PRELUDE = '{% load ontask_tags %}'


def make_translate(*args, **keywords) -> Callable:
    """Apply multiple character substitutions.

    Auxiliary function to define a translator that applies multiple character
    substitutions at once.

    Taken from "Python Cookbook, 2nd Edition by David Ascher, Anna Ravenscroft,
    Alex Martelli", Section 1.18

    :param args: Dictionary
    :param keywords:
    :return: A function that uses the given dictionary to apply multiple
    changes to a string
    """
    adict = dict(*args, **keywords)
    re_exec = re.compile(r'|'.join(map(re.escape, adict)))

    def one_translate(match) -> str:
        """Translate match."""
        return adict[match.group(0)]

    def translate(text: str) -> str:
        """Apply regext substitution."""
        return re_exec.sub(one_translate, text)

    return translate


# Dictionary to translate non-alphanumeric symbols into alphanumeric pairs
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# !#$%&()*+,-./:;<=>?@[\]^_`{|}~
# abcdefghijklmnopqrstuvwxyz01234
TR_DICT = {
    '!': '_a',
    '#': '_b',
    '$': '_c',
    '%': '_d',
    '&': '_e',
    '(': '_f',
    ')': '_g',
    '*': '_h',
    '+': '_i',
    ',': '_j',
    '-': '_k',
    '.': '_l',
    '/': '_m',
    ':': '_n',
    ';': '_o',
    '<': '_p',
    '=': '_q',
    '>': '_r',
    '?': '_s',
    '@': '_t',
    '[': '_u',
    '\\': '_v',
    ']': '_w',
    '^': '_x',
    '_': '_y',
    '`': '_z',
    '{': '_0',
    '|': '_1',
    '}': '_2',
    '~': '_3',
    ' ': '_4',
}

TR_ITEM = make_translate(TR_DICT)
RTR_ITEM = make_translate(dict((val, key) for key, val in TR_DICT.items()))


def _change_variable_name(match) -> str:
    """Change variable name using the match object from re.

    :param match:
    :return: String with the variable name translated
    """
    re_dict = match.groupdict()

    if '{% ot_insert_report' in re_dict.get('mup_pre'):
        # Match is an ot_insert_report macro
        args = shlex.split(re_dict['args'])
        return (
            match.group('mup_pre')
            + ' '.join(['"' + _translate(cname) + '"' for cname in args])
            + match.group('mup_post'))

    return (
        match.group('mup_pre')
        + _translate(match.group('vname'))
        + match.group('mup_post'))


def _change_unescape_variable_name(match) -> str:
    """Change unescaped variable name using the match object from re.

    :param match:
    :return: String with the variable name translated
    """
    re_dict = match.groupdict()

    if '{% ot_insert_report' in re_dict.get('mup_pre'):
        # Match is an ot_insert_report macro
        args = [
            arg.replace(
                '&amp;', '&').replace(
                '&lt;', '<').replace(
                '&gt;', '>').replace(
                '&quot;', '"').replace(
                '&#39;', "'")
            for arg in shlex.split(re_dict['args'])]

        return (
            match.group('mup_pre')
            + ' '.join(['"' + _translate(cname) + '"' for cname in args])
            + match.group('mup_post'))

    var_name = match.group('vname').replace(
        '&amp;', '&').replace(
        '&lt;', '<').replace(
        '&gt;', '>').replace(
        '&quot;', '"').replace(
        '&#39;', "'")
    return (
        match.group('mup_pre')
        + _translate(var_name)
        + match.group('mup_post'))


def _translate(varname: str) -> str:
    """Apply several translations to a variable name.

    Function that given a string representing a variable name applies a
    translation to each of the non-alphanumeric characters in that name.
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
    return TR_ITEM(varname)


def _clean_whitespace(template_text: str) -> str:
    """Remove whitespace before and after conditionals.

    Function to detect new lines before and after the conditional template
    macros and removes it.

    :param template_text: Initial template text
    :return: Modified template text
    """
    # Loop over the regular expressions and apply them to the given text
    for rexp, replace in WHITE_SPACE_RES:
        template_text = rexp.sub(replace, template_text)

    return template_text


def render_rubric_criteria(action: models.Action, context: Dict) -> List[List]:
    """Calculate the list of elements [criteria, feedback] for action.

    :param action: Action being manipulated (Rubric)
    :param context: Dictionary with values
    :return: List of HTML snippets, one per criteria.
    """
    criteria = [acc.column for acc in action.column_condition_pair.all()]
    cells = action.rubric_cells.all()
    text_sources = []

    for criterion in criteria:
        if not (c_value := context.get(_translate(escape(criterion.name)))):
            # Skip criteria with no values
            continue

        value_idx = criterion.categories.index(c_value)
        if not (cell := cells.filter(
            column=criterion,
            loa_position=value_idx).first()
        ):
            continue
        text_sources.append([criterion.name, cell.feedback_text])

    return text_sources


def render_action_template(
    template_text: str,
    context_dict: Mapping,
    action: models.Action = None,
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

    The solution:
    1) Parse the template and detect the use of all variables.

    2) For each variable, transform its name into a legal one
       for Jinja (starts with letter followed by letter, number or '_' *)

       The transformation is based on:
       - Every non-letter or number is replaced by '_' followed by a
         letter/number, as specified by the global dictionary.

       - If the original variable does not start by a letter, insert a prefix.

    3) Apply the same transformation for the keys in the given dictionary

    4) Execute the new template with the new dictionary and return the result.

    :param template_text: Text in the template to be rendered
    :param context_dict: Dictionary used by Jinja to evaluate the template
    :param action: Action object to insert in the context in case it is
    needed by any other custom template.
    :return: The rendered template
    """
    # Steps 1 and 2. Apply the translation process to all variables that
    # appear in the template text
    new_template_text = template_text
    for regex in models.VAR_USE_RES:
        if action and action.has_html_text:
            new_template_text = regex.sub(
                _change_unescape_variable_name,
                new_template_text)
        else:
            new_template_text = regex.sub(
                _change_variable_name,
                new_template_text)

    # Step 2.2 Remove pre-and post white space from the {% if %} and
    # {% endif %} conditions (to reduce white space when using non HTML
    # content).
    new_template_text = _clean_whitespace(new_template_text)

    # Step 3. Apply the translation process to the context keys
    new_context = {
        _translate(key): str_val
        for key, str_val in list(context_dict.items())
    }

    # If the number of elements in the two dictionaries is different, we have
    #  a case of collision in the translation. Need to stop immediately.
    assert len(context_dict) == len(new_context)

    if ACTION_CONTEXT_VAR in new_context:
        raise Exception(_('Name {0} is reserved.').format(ACTION_CONTEXT_VAR))
    new_context[ACTION_CONTEXT_VAR] = action

    if VIZ_NUMBER_CONTEXT_VAR in new_context:
        raise Exception(_('Name {0} is reserved.').format(
            VIZ_NUMBER_CONTEXT_VAR,
        ))
    new_context[VIZ_NUMBER_CONTEXT_VAR] = 0

    # Step 4. Return the rendering of the new elements
    return Template(
        _ONTASK_TEMPLATE_PRELUDE + new_template_text,
    ).render(Context(new_context))
