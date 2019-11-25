# -*- coding: utf-8 -*-

"""View to serve an action through a URL provided to learners."""

import random
from typing import List, Mapping, Tuple

from ontask import models
from ontask.action.forms import FIELD_PREFIX
from ontask.dataops.sql.row_queries import update_row


def extract_survey_questions(
    action: models.Action, user_seed: str,
) -> List[models.ActionColumnConditionTuple]:
    """Extract the set of questions to include in a survey.

    :param action: Action being executed
    :param user_seed: Seed so that it can be replicated several times and
    is user dependent
    :return: List of ColumnCondition pairs
    """
    # Get the active columns attached to the action
    colcon_items = [
        pair for pair in action.column_condition_pair.all()
        if pair.column.is_active
    ]

    if action.shuffle:
        # Shuffle the columns if needed
        random.seed(user_seed)
        random.shuffle(colcon_items)

    return colcon_items


def survey_update_row_values(
    action: models.Action,
    colcon_items,
    show_key: bool,
    form_data: Mapping,
    where_field: str,
    where_value: str,
    context: Mapping,
) -> Tuple[List, List]:
    """Collect the values of the survey and update the DB.

    :param action: Action being executed
    :param colcon_items: Pairs colum - condition
    :param show_key: Should key columns be considered?
    :param form_data: Input data received in the form
    :param where_field_value: key, value to locate the user
    :param context: Condition values
    :return: Zip iterator with pairs (name, value)
    """
    keys = []
    values = []
    # Create the SET name = value part of the query
    for idx, colcon in enumerate(colcon_items):
        if colcon.column.is_key and not show_key:
            # If it is a learner request and a key column, skip
            continue

        # Skip the element if there is a condition and it is false
        if colcon.condition and not context[colcon.condition.name]:
            continue

        field_value = form_data[FIELD_PREFIX + '{0}'.format(idx)]
        if colcon.column.is_key:
            # Remember one unique key for selecting the row
            where_field = colcon.column.name
            where_value = field_value
            continue

        keys.append(colcon.column.name)
        values.append(field_value)

    # Execute the query
    update_row(
        action.workflow.get_data_frame_table_name(),
        keys,
        values,
        filter_dict={where_field: where_value},
    )

    # Recompute all the values of the conditions in each of the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for act in action.workflow.actions.all():
        act.update_n_rows_selected()

    return keys, values
