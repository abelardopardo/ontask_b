# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template
from django.template.loader import render_to_string
from validate_email import validate_email

import dataops.formula_evaluation
from action.models import Condition
from dataops import pandas_db, ops
from ontask import OntaskException
from workflow.models import Workflow


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

    # Get the attributes from the workflow
    attributes = workflow.attributes

    template = Template(action.content)
    extra_template = None
    if extra_string:
        # Create a template for the extra string
        try:
            extra_template = Template(extra_string)
        except Exception, e:
            return 'Syntax error detected in the subject. ' + e.message

    # Step 2: Get the row of data from the DB
    try:
        cond_filter = Condition.objects.get(action__id=action.id,
                                            is_filter=True)
    except ObjectDoesNotExist:
        cond_filter = None

    # Step 3: Get the matrix data
    result = []
    data_matrix = pandas_db.get_table_data(workflow.id, cond_filter)

    # Check if the values in the email column are correct emails
    try:
        correct_emails = all([validate_email(x[col_idx]) for x in data_matrix])
        if not correct_emails:
                # column has incorrect email addresses
                return 'The column with email addresses has incorrect values.'
    except TypeError:
        return 'The column with email addresses has incorrect values'

    for row in data_matrix:

        # Get the dict(col_name, value)
        row_values = dict(zip(col_names, row))

        # Step 3: Evaluate all the conditions
        condition_eval = {}
        for condition in Condition.objects.filter(action__id=action.id):
            if condition.is_filter:
                # Filter can be skipped in this stage
                continue

            # Evaluate the condition
            condition_eval[condition.name] = \
                dataops.formula_evaluation.evaluate_top_node(
                    condition.formula,
                    row_values
                )

        # Step 4: Create the context with the attributes, the evaluation of the
        # conditions and the values of the columns.
        context = dict(dict(row_values, **condition_eval), **attributes)

        # Step 5: run the template with the given context
        # Render the text and append to result
        partial_result = [template.render(Context(context))]

        # If there is extra message, render with context and create tuple
        if extra_string:
            partial_result.append(extra_template.render(Context(context)))

        # If column_name was given (and it exists), create a tuple with that
        # element as the third component
        if col_idx != -1:
            partial_result.append(row_values[col_names[col_idx]])

        # Append result
        result.append(partial_result)

    return result


def evaluate_row(action, row_idx):
    """
    Given an action object and a row index:
    1) Access the attached workflow
    2) Obtain the row of data from the appropriate data frame
    3) Evaluate the conditions with respect to the values in the row
    4) Create a context with the result of evaluating the conditions,
       attributes and column names to values
    5) Run the template with the context
    6) Return the resulting object (HTML?)

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :param row_idx: Either an integer (row index), or a pair key=value to
           filter
    :return:
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
        row_values = pandas_db.get_table_row_by_key(workflow.id,
                                                    cond_filter,
                                                    row_idx)
    if row_values is None:
        # No rows satisfy the given condition
        return None

    # Step 3: Evaluate all the conditions
    condition_eval = {}
    condition_anomalies = []
    for condition in Condition.objects.filter(action__id=action.id):
        if condition.is_filter:
            # Filter can be skipped in this stage
            continue

        # Evaluate the condition
        try:
            condition_eval[condition.name] = \
                dataops.formula_evaluation.evaluate_top_node(
                    condition.formula,
                    row_values
                )
        except OntaskException, e:
            condition_anomalies.append(e.value)

    # If any of the variables was incorrectly evaluated, we replace the
    # content and replace it by something noting this anomaly
    if condition_anomalies:
        return render_to_string('action/incorrect_preview.html',
                                {'missing_values': condition_anomalies})

    # Step 4: Create the context with the attributes, the evaluation of the
    # conditions and the values of the columns.
    attributes = workflow.attributes
    context = dict(dict(row_values, **condition_eval), **attributes)

    # Step 5: run the template with the given context
    # First create the template with the string stored in the action
    template = Template(action.content)

    # Render the text
    return template.render(Context(context))
