# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals, print_function

import re
import string

from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.html import escape
from validate_email import validate_email

import dataops.formula_evaluation
from action.forms import EnterActionIn
from action.models import Condition
from dataops import pandas_db, ops
from ontask import OntaskException
from workflow.models import Workflow

# Variable name to store the workflow ID in the context used to render a
# template
action_context_var = 'ONTASK_ACTION_CONTEXT_VARIABLE___'
viz_number_context_var = 'ONTASK_VIZ_NUMBER_CONTEXT_VARIABLE___'

def make_xlat(*args, **kwds):
    """
    Auxuliary function to define a translator that applies multiple character
    substitutions at once.

    Taken from "Python Cookbook, 2nd Edition by David Ascher, Anna Ravenscroft,
    Alex Martelli", Section 1.18

    :param args: Dictionary
    :param kwds:
    :return: A function that uses the given dictionary to apply multiple
    changes to a string
    """
    adict = dict(*args, **kwds)
    rx = re.compile('|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]

    def xlat(text):
        return rx.sub(one_xlat, text)

    return xlat


# Dictionary to translate non alphanumeric symbols into alphanumeric pairs
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
# abcdefghijklmnopqrstuvwxyzABCDEFG
tr_item = make_xlat({
    '!': '_a', '"': '_b', '#': '_c', '$': '_d', '%': '_e', '&': '_f',
    "'": "_g", '(': '_h', ')': '_i', '*': '_j', '+': '_k', ',': '_l',
    '-': '_m', '.': '_n', '/': '_o', ':': '_p', ';': '_q', '<': '_r',
    '=': '_s', '>': '_t', '?': '_u', '@': '_v', '[': '_w', '\\': '_x',
    ']': '_y', '^': '_z', '_': '_0', '`': '_1', '{': '_2', '|': '_3',
    '}': '_4', '~': '_5', ' ': '_6',
})


def translate(varname):
    """
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
    if not varname[0] in string.letters or varname.startswith('OT_'):
        varname = 'OT_' + varname

    # Return the new variable name surrounded by the detected marks.
    return tr_item(varname)


def render_template(template_text, context_dict, action=None):
    """
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

    # Regular expressions detecting the use of a variable, or the
    # presence of a "{% MACRONAME variable %} construct in a string (template)
    var_use_res = [
        re.compile('(?P<mup_pre>{{\s+)(?P<vname>.+?)(?P<mup_post>\s+\}\})'),
        re.compile('(?P<mup_pre>{%\s+if\s+)(?P<vname>.+?)(?P<mup_post>\s+%\})')
    ]

    # Steps 1 and 2. Apply the tranlation process to all variables that
    # appear in the the template text
    new_template_text = template_text
    for rexpr in var_use_res:
        new_template_text = rexpr.sub(
            lambda m: m.group('mup_pre') + \
                      translate(m.group('vname')) + \
                      m.group('mup_post'),
            new_template_text)
    new_template_text = '{% load vis_include %}' + new_template_text

    # Step 3. Apply the translation process to the context keys
    new_context = dict([(translate(escape(x)), y)
                        for x, y in context_dict.items()])

    # If the number of elements in the two dictionaries is different, we have
    #  a case of collision in the translation. Need to stop immediately.
    assert len(context_dict) == len(new_context)

    if action_context_var in new_context:
        raise Exception('Name {0} is reserved.'.format(action_context_var))
    new_context[action_context_var] = action

    if viz_number_context_var in new_context:
        raise Exception('Name {0} is reserved.'.format(viz_number_context_var))
    new_context[viz_number_context_var] = 0

    # Step 4. Return the redering of the new elements
    return Template(new_template_text).render(Context(new_context))


def evaluate_action(action, extra_string, column_name):
    """
    Given an action object and an optional string:
    1) Access the attached workflow
    2) Obtain the data from the appropriate data frame
    3) Loop over each data row and
      3.1) Evaluate the conditions with respect to the values in the row
      3.2) Create a context with the result of evaluating the conditions,
           attributes and column names to values
      3.3) Run the template with the context
      3.4) Run the optional string argument with the template and the context
      3.5) Select the optional column_name
    6) Return the resulting objects:
       List of (HTMLs body, extra string, column name value)
        or an error message

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :param extra_string: An extra string to process (something like the email
           subject line) with the same dictionary as the text in the action.
    :param column_name: Column from where to extract the special value (
           typically the email address) and include it in the result.
    :return: list of lists resulting from the evaluation of the action
    """

    # Step 1: Get the workflow to access the data and prepare data
    workflow = Workflow.objects.get(pk=action.workflow.id)
    col_names = workflow.get_column_names()
    col_idx = -1
    if column_name and column_name in col_names:
        col_idx = col_names.index(column_name)

    # Step 2: Get the row of data from the DB
    try:
        cond_filter = Condition.objects.get(action__id=action.id,
                                            is_filter=True)
    except ObjectDoesNotExist:
        cond_filter = None

    # Step 3: Get the table data
    result = []
    data_frame = pandas_db.get_subframe(workflow.id, cond_filter)

    # Check if the values in the email column are correct emails
    try:
        correct_emails = all([validate_email(x)
                              for x in data_frame[column_name]])
        if not correct_emails:
            # column has incorrect email addresses
            return 'The column with email addresses has incorrect values.'
    except TypeError:
        return 'The column with email addresses has incorrect values'

    for _, row in data_frame.iterrows():

        # Get the dict(col_name, value)
        row_values = dict(zip(col_names, row))

        # Step 3: Evaluate all the conditions
        condition_eval = {}
        for condition in Condition.objects.filter(
                action__id=action.id
        ).values('is_filter', 'formula', 'name'):
            if condition['is_filter']:
                # Filter can be skipped in this stage
                continue

            # Evaluate the condition
            condition_eval[condition['name']] = \
                dataops.formula_evaluation.evaluate_top_node(
                    condition['formula'],
                    row_values
                )

        # Step 4: Create the context with the attributes, the evaluation of the
        # conditions and the values of the columns.
        attributes = workflow.attributes
        context = dict(dict(row_values, **condition_eval), **attributes)

        # Step 5: run the template with the given context
        # Render the text and append to result
        try:
            partial_result = [render_template(action.content,
                                              context,
                                              action)]
        except Exception as e:
            return 'Syntax error detected in the action text. ' + e.message

        # If there is extra message, render with context and create tuple
        if extra_string:
            try:
                partial_result.append(render_template(extra_string, context))
            except Exception as e:
                return 'Syntax error detected in the subject. ' + e.message

        # If column_name was given (and it exists), create a tuple with that
        # element as the third component
        if col_idx != -1:
            partial_result.append(row_values[col_names[col_idx]])

        # Append result
        result.append(partial_result)

    return result


def evaluate_row(action, row_idx):
    """
    Given an action and a row index, evaluate the content of the action for
    that index. The evaluation depends on the action type.

    Given an action object and a row index:
    1) Access the attached workflow
    2) Obtain the row of data from the appropriate data frame
    3) Process further depending on the type of action

    :param action: Action object
    :param row_idx: Row index to use for evaluation
    :return HTML content resulting from the evaluation
    """

    # Step 1: Get the workflow to access the data. No need to check for
    # locking information as it has been checked upstream.
    workflow = Workflow.objects.get(pk=action.workflow.id)

    # Step 2: Get the row of data from the DB
    try:
        cond_filter = Condition.objects.get(action__id=action.id,
                                            is_filter=True)
    except ObjectDoesNotExist:
        cond_filter = None

    # If row_idx is an integer, get the data by index, otherwise, by key
    if isinstance(row_idx, int):
        row_values = ops.get_table_row_by_index(workflow,
                                                cond_filter,
                                                row_idx)
    else:
        row_values = pandas_db.get_table_row_by_key(workflow,
                                                    cond_filter,
                                                    row_idx)
    if row_values is None:
        # No rows satisfy the given condition
        return None

    # Invoke the appropriate function depending on the action type
    if action.is_out:
        return evaluate_row_out(action, row_values)

    return evaluate_row_in(action, row_values)


def evaluate_row_out(action, row_values):
    """
    Given an action object and a row index:
    1) Evaluate the conditions with respect to the values in the row
    2) Create a context with the result of evaluating the conditions,
       attributes and column names to values
    3) Run the template with the context
    4) Return the resulting object (HTML?)

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :param row_values: dictionary with the pairs name, value
    :return: String with the HTML content resulting from the evaluation
    """

    # Step 1: Evaluate all the conditions
    condition_eval = {}
    condition_anomalies = []
    for condition in Condition.objects.filter(
            action__id=action.id
    ).values('name', 'is_filter', 'formula'):
        if condition['is_filter']:
            # Filter can be skipped in this stage
            continue

        # Evaluate the condition
        try:
            condition_eval[condition['name']] = \
                dataops.formula_evaluation.evaluate_top_node(
                    condition['formula'],
                    row_values
                )
        except OntaskException as e:
            condition_anomalies.append(e.value)

    # If any of the variables was incorrectly evaluated, we replace the
    # content and replace it by something noting this anomaly
    if condition_anomalies:
        return render_to_string('action/incorrect_preview.html',
                                {'missing_values': condition_anomalies})

    # Step 2: Create the context with the attributes, the evaluation of the
    # conditions and the values of the columns.
    attributes = action.workflow.attributes
    context = dict(dict(row_values, **condition_eval), **attributes)

    # Step 3: run the template with the given context
    # First create the template with the string stored in the action
    try:
        result = render_template(action.content, context, action)
    except TemplateSyntaxError as e:
        return render_to_string('action/syntax_error.html',
                                {'msg': e.message})

    # Step 4: Render the text
    return result


def evaluate_row_in(action, row_values):
    """
    Given an action IN object and a row index:
    1) Create the form and the context
    2) Run the template with the context
    3) Return the resulting object (HTML?)

    :param action: Action object.
    :param row_values: Dictionary with pairs name/value
    :return: String with the HTML content resulting from the evaluation
    """

    # Get the active columns attached to the action
    columns = [c for c in action.columns.all() if c.is_active]

    # Get the row values.
    selected_values = [row_values[c.name] for c in columns]

    form = EnterActionIn(None, columns=columns, values=selected_values)

    # Render the form
    return Template(
        """<div align="center" class=≠≠≠=">
             <h4 class="page-header"><strong>{{ action.name }}</strong></h4>
             <p class="lead">{{ description_text }}</p>
             {% load crispy_forms_tags %}{{ form|crispy }}
           </div>"""
    ).render(Context({'form': form,
                      'description_text': action.description_text}))


def run(*script_args):
    """
    Script for testing purposes
    :param script_args:
    :return:
    """
    del script_args

    template = """
    hi --{{ one }}--
    --{% if var1 %}var1{% endif %}--
    --{% if var2 %}var2{% endif %}-- 
    --{% if !"# %}var3{% endif %}--
    --{% if $%& %}var4{% endif %}--
    --{% if '() %}var5{% endif %}--
    --{{ +,- }}--
    --{{ ./: }}--
    --{{ ;<= }}--
    --{{ >?@ }}--
    --{{ [\] }}--
    --{{ ^_` }}--
    --{{ {|}~ }}--
    --{{ this one has spaces }}--
    --{{ OT_ The prefix }}--
    --{{ OT_The prefix 2 }}--
    """

    template = u'<p>Hi&nbsp;{{ !"#$%&amp;()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~ }}</p>'

    context = {
        'one': 1,
        'var1': True,
        'var2': True,
        '!"#': True,
        '$%&': True,
        "'()": True,
        '+,-': 'var6',
        './:': 'var7',
        ';<=': 'var8',
        '>?@': 'var9',
        '[\]': 'var10',
        '^_`': 'var11',
        '{|}~': 'var12',
        'this one has spaces': 'The spaces are not a problem',
        'OT_ The prefix': 'Prefix solved.',
        'OT_The prefix 2': 'Prefix 2 solved',
        'The prefix 2': 'This should NOT appear. ERROR',
    }
    context = {
        u'!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~': u'Carmelo Coton',
    }

    print(escape(context.items()[0][0]))
    print(render_template(template, context))


