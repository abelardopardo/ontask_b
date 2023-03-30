# -*- coding: utf-8 -*-

"""Functions to clone action/conditions."""
import copy

from ontask import models
from ontask.dataops import formula


def do_clone_condition(
    user,
    condition: models.Condition,
    new_action: models.Action = None,
    new_name: str = None,
):
    """Clone a condition.

    Function to clone a condition and change action and/or name

    :param user: User executing the operation
    :param condition: Condition to clone
    :param new_action: New action to point
    :param new_name: New name
    :return: Nothing
    """
    old_id = condition.id
    old_name = condition.name

    if new_name is None:
        new_name = condition.name
    if new_action is None:
        new_action = condition.action

    new_condition = models.Condition(
        name=new_name,
        workflow=condition.workflow,
        description_text=condition.description_text,
        action=new_action,
        formula=copy.deepcopy(condition.formula),
        n_rows_selected=condition.n_rows_selected)
    new_condition.save()

    try:
        # Update the many to many field.
        new_condition.columns.set(new_condition.action.workflow.columns.filter(
            name__in=formula.get_variables(new_condition.formula),
        ))
    except Exception as exc:
        new_condition.delete()
        raise exc

    condition.log(
        user,
        models.Log.CONDITION_CLONE,
        id_old=old_id,
        name_old=old_name)


def do_clone_filter(
    user,
    filter_obj: models.Filter,
    new_action: models.Action = None,
):
    """Clone a filter.

    Function to clone a filter and change action.

    :param user: User executing the operation
    :param filter_obj: Condition to clone
    :param new_action: New action to point
    :return: Nothing
    """
    old_id = filter_obj.id

    new_filter = models.Filter(
        workflow=filter_obj.workflow,
        description_text=filter_obj.description_text,
        action=new_action,
        formula=copy.deepcopy(filter_obj.formula),
        n_rows_selected=filter_obj.n_rows_selected)
    new_filter.save()

    try:
        # Update the many to many field.
        new_filter.columns.set(new_filter.workflow.columns.filter(
            name__in=formula.get_variables(new_filter.formula),
        ))
    except Exception as exc:
        new_filter.delete()
        raise exc

    filter_obj.log(
        user,
        models.Log.CONDITION_CLONE,
        id_old=old_id)
