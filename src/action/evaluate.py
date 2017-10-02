# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.template import Context, Template

from workflow.models import Workflow
from action.models import Condition
from dataops import panda_db


def evaluate_action(action, **kargs):
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
       List of either HTMLs and optionally a tuple with the corresponding
        rendered extra string and column name value (if given)

    :param action: Action object with pointers to conditions, filter,
                   workflow, etc.
    :return: list of lists resulting from the evaluation of the action
    """

    # Get the optional args
    extra_string = kargs.pop('extra_string', None)
    column_name = kargs.pop('column_name', None)

    # Step 1: Get the workflow to access the data and prepare data
    workflow = Workflow.objects.get(pk=action.workflow.id)
    col_names = json.loads(workflow.column_names)
    col_idx = -1
    if column_name and column_name in col_names:
        col_idx = col_names.index(column_name)

    attributes = json.loads(workflow.attributes)
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
        filter = Condition.objects.get(action__id=action.id,
                                       is_filter=True)
    except Condition.DoesNotExist:
        filter = None

    # Step 3: Get the matrix data and loop over it
    result = []
    data_matrix = panda_db.get_table_data(workflow.id, filter)
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
            condition_eval[condition.name] = panda_db.evaluate_top_node(
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
    :param row_idx: row index in the data frame to be processed
    :return:
    """

    # Step 1: Get the workflow to access the data
    workflow = Workflow.objects.get(pk=action.workflow.id)

    # Step 2: Get the row of data from the DB
    try:
        filter = Condition.objects.get(action__id=action.id,
                                       is_filter=True)
    except Condition.DoesNotExist:
        filter = None

    row_values = panda_db.get_table_row(workflow.id, filter, row_idx)

    # Step 3: Evaluate all the conditions
    condition_eval = {}
    for condition in Condition.objects.filter(action__id=action.id):
        if condition.is_filter:
            # Filter can be skipped in this stage
            continue

        # Evaluate the condition
        condition_eval[condition.name] = panda_db.evaluate_top_node(
            condition.formula,
            row_values
        )

    # Step 4: Create the context with the attributes, the evaluation of the
    # conditions and the values of the columns.
    context = dict(dict(row_values, **condition_eval),
                   **json.loads(workflow.attributes))

    # Step 5: run the template with the given context
    # First create the template with the string stored in the action
    template = Template(action.content)

    # Render the text
    return template.render(Context(context))
