# -*- coding: utf-8 -*-

"""Service functions to handle row creation/edition.."""
from typing import Any, List

from django.db import transaction

from ontask import models
from ontask.core import checks
from ontask.dataops import sql


def create_row(workflow: models.Workflow, row_values: List[Any]):
    """Create an additional row with the information in the form.

    :param workflow: Workflow object being processed.
    :param row_values: List of values to store.
    :return: Nothing.
    """
    # Create the query to update the row
    columns = workflow.columns.all()
    column_names = [col.name for col in columns]

    with transaction.atomic():
        # Insert the new row in the db
        sql.insert_row(
            workflow.get_data_frame_table_name(),
            column_names,
            row_values)
        # verify that the "key" property is maintained in all the
        # columns.
        checks.check_key_columns(workflow)

    # Update number of rows
    workflow.nrows += 1
    workflow.save(update_fields=['nrows'])

    # Recompute all the values of the conditions in each of the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for act in workflow.actions.all():
        act.update_selected_row_counts()


def update_row_values(
    workflow: models.Workflow,
    update_key: str,
    update_val: Any,
    row_values: List[Any],
):
    """Update a row with the information in the form.

    :param workflow: Workflow object being processed.
    :param update_key: Column name to use to select row.
    :param update_val: Column value to select row.
    :param row_values: List of values to store in the row
    :return: Nothing.
    """
    # Create the query to update the row
    column_names = [col.name for col in workflow.columns.all()]
    with transaction.atomic():
        # Update the row in the db
        sql.update_row(
            workflow.get_data_frame_table_name(),
            column_names,
            row_values,
            filter_dict={update_key: update_val})
        # verify that the "key" property is maintained in all the
        # columns.
        checks.check_key_columns(workflow)

    # Recompute all the values of the conditions in each of the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for act in workflow.actions.all():
        act.update_selected_row_counts()
