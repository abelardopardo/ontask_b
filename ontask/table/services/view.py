"""Functions to support the display of a view."""
from typing import Optional

from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.condition.services import do_clone_filter
from ontask.dataops import formula
from ontask.table.services.errors import OnTaskTableCloneError


def do_clone_view(
    user,
    view: models.View,
    new_workflow: models.Workflow = None,
    new_name: str = None,
) -> Optional[models.View]:
    """Clone a view.

    :param user: User requesting the operation
    :param view: Object to clone
    :param new_workflow: Non-empty if it has to point to a new workflow
    :param new_name: Non-empty if it has to be renamed.
    :result: New clone object
    """
    if view is None:
        return None

    id_old = view.id
    name_old = view.name

    # Proceed to clone the view
    if new_name is None:
        new_name = view.name
    if new_workflow is None:
        new_workflow = view.workflow

    new_view = models.View(
        name=new_name,
        description_text=view.description_text,
        workflow=new_workflow,
        filter=do_clone_filter(user, view.filter, new_workflow))
    new_view.save()

    try:
        # Update the many-to-many field.
        new_view.columns.set(list(view.columns.all()))
    except Exception:
        raise OnTaskTableCloneError(
            message=_('Error while cloning table view.'),
            to_delete=[new_view]
        )

    view.log(
        user,
        models.Log.VIEW_CLONE,
        id_old=id_old,
        name_old=name_old)

    return new_view


def save_view_form(
    user,
    workflow: models.Workflow,
    view: models.View,
    filter_obj: Optional[models.Filter] = None,
):
    """Save the data attached to a view.

    :param user: user requesting the operation
    :param workflow: Workflow being processed
    :param view: View being processed.
    :param filter_obj: Filter object containing the formula
    :return: AJAX Response
    """
    view.workflow = workflow

    if not formula.is_empty(filter_obj.formula):
        filter_obj.workflow = workflow
        filter_obj.save()
        filter_obj.columns.set(workflow.columns.filter(
            name__in=formula.get_variables(filter_obj.formula)))
        view.filter = filter_obj

    view.save()
    view.log(
        user,
        models.Log.VIEW_CREATE if view.id is None else models.Log.VIEW_EDIT)
