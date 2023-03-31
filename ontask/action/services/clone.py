# -*- coding: utf-8 -*-

"""Functions to clone action/conditions."""
import copy

from ontask import models
from ontask.condition import services


def do_clone_action(
    user,
    action: models.Action,
    new_workflow: models.Workflow = None,
    new_name: str = None,
):
    """Clone an action.

    Function that given an action clones it and changes workflow and name

    :param user: User executing the operation
    :param action: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """
    old_id = action.id
    old_name = action.name

    if new_name is None:
        new_name = action.name
    if new_workflow is None:
        new_workflow = action.workflow

    # Clone the filter
    new_filter = None
    if action.filter is not None:
        if getattr(action.filter, 'view', None):
            # The filter is in a view
            new_filter = new_workflow.views.get(
                name=action.filter.view.name).filter
        else:
            new_filter = services.do_clone_filter(
                user,
                action.filter,
                new_workflow)

    new_action = models.Action(
        name=new_name,
        description_text=action.description_text,
        workflow=new_workflow,
        last_executed_log=None,
        action_type=action.action_type,
        serve_enabled=action.serve_enabled,
        active_from=action.active_from,
        active_to=action.active_to,
        rows_all_false=copy.deepcopy(action.rows_all_false),
        text_content=action.text_content,
        target_url=action.target_url,
        shuffle=action.shuffle,
        filter=new_filter)
    new_action.save()

    try:
        # Clone the column/condition pairs field.
        for acc_tuple in action.column_condition_pair.all():
            cname = acc_tuple.condition.name if acc_tuple.condition else None
            models.ActionColumnConditionTuple.objects.get_or_create(
                action=new_action,
                column=new_action.workflow.columns.get(
                    name=acc_tuple.column.name),
                condition=new_action.conditions.filter(name=cname).first(),
            )

        # Clone the rubric cells if any
        for rubric_cell in action.rubric_cells.all():
            models.RubricCell.objects.create(
                action=new_action,
                column=new_action.workflow.columns.get(
                    name=rubric_cell.column.name),
                loa_position=rubric_cell.loa_position,
                description_text=rubric_cell.description_text,
                feedback_text=rubric_cell.feedback_text)

        # Clone the conditions
        for condition in action.conditions.all():
            services.do_clone_condition(user, condition, new_action)

        # Update
        new_action.save()
    except Exception as exc:
        new_action.delete()
        raise exc

    # Log event
    action.log(
        user,
        models.Log.ACTION_CLONE,
        id_old=old_id,
        name_old=old_name)

    return new_action
