# -*- coding: utf-8 -*-

"""Functions to manipulate workflow CRUD ops."""
import copy
from typing import Dict

from django import http
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import OnTaskServiceException, create_new_name, models
from ontask.action.services.clone import do_clone_action
from ontask.core.session_ops import store_workflow_in_session
from ontask.dataops.sql import clone_table
from ontask.table.services import do_clone_view
from ontask.workflow import forms
from ontask.workflow.services.column_crud import do_clone_column_only


def save_workflow_form(
    request: http.HttpRequest,
    form: forms.WorkflowForm,
) -> http.JsonResponse:
    """Save the workflow to create a form.

    :param request: Received HTTP Request
    :param form: Form used to get the Workflow parameters
    :return: JSON Response
    """
    if form.instance.id:
        log_type = models.Log.WORKFLOW_UPDATE
        redirect_url = ''
        # Save the instance
        workflow_item = form.save()
    else:
        # This is a new instance!
        form.instance.user = request.user
        workflow_item = form.save()
        workflow_item.nrows = 0
        workflow_item.ncols = 0
        log_type = models.Log.WORKFLOW_CREATE
        redirect_url = reverse('dataops:uploadmerge')

        # Store in session
        store_workflow_in_session(request, workflow_item)

    workflow_item.log(request.user, log_type)
    return http.JsonResponse({'html_redirect': redirect_url})


def get_detail_context(workflow: models.Workflow) -> Dict:
    """Create the context to render the details page.

    :param workflow: Workflow being manipulated
    :return: Dictionary to render the details page
    """
    context = {
        'workflow': workflow,
        'table_info': None}
    if workflow.has_table():
        context['table_info'] = {
            'num_rows': workflow.nrows,
            'num_cols': workflow.ncols,
            'num_actions': workflow.actions.count(),
            'num_attributes': len(workflow.attributes)}

    # put the number of key columns in the context
    context['num_key_columns'] = workflow.columns.filter(
        is_key=True,
    ).count()

    # Guarantee that column position is set for backward compatibility
    columns = workflow.columns.all()
    if any(col.position == 0 for col in columns):
        # At least a column has index equal to zero, so reset all of them
        for idx, col in enumerate(columns):
            col.position = idx + 1
            col.save()

    return context


def get_index_context(user) -> Dict:
    """Create the context to render the details page.

    :param user: User making the request
    :return: Dictionary to render the index page
    """
    workflows = user.workflows_owner.all() | user.workflows_shared.all()
    workflows = workflows.distinct()

    # Get the queryset for those with start and those without
    workflows_star = workflows.filter(star__in=[user])
    workflows_no_star = workflows.exclude(star__in=[user])

    # We include the table only if it is not empty.
    return {
        'workflows_star': workflows_star.order_by('name'),
        'workflows': workflows_no_star.order_by('name'),
        'nwflows': len(workflows)}


def do_clone_workflow(user, workflow: models.Workflow) -> models.Workflow:
    """Clone a workflow.

    :param user: User performing the operation
    :param workflow: source workflow
    :return: Cloned object
    """
    new_workflow = models.Workflow(
        user=workflow.user,
        name=create_new_name(
            workflow.name,
            models.Workflow.objects.filter(
                Q(user=workflow.user) | Q(shared=workflow.user)),
        ),
        description_text=workflow.description_text,
        nrows=workflow.nrows,
        ncols=workflow.ncols,
        attributes=copy.deepcopy(workflow.attributes),
        query_builder_ops=copy.deepcopy(workflow.query_builder_ops),
        luser_email_column_md5=workflow.luser_email_column_md5,
        lusers_is_outdated=workflow.lusers_is_outdated)
    new_workflow.save()

    try:
        new_workflow.shared.set(list(workflow.shared.all()))
        new_workflow.lusers.set(list(workflow.lusers.all()))

        # Clone the columns
        for item_obj in workflow.columns.all():
            do_clone_column_only(item_obj, new_workflow=new_workflow)

        # Update the luser_email_column if needed:
        if workflow.luser_email_column:
            new_workflow.luser_email_column = new_workflow.columns.get(
                name=workflow.luser_email_column.name,
            )

        # Clone the DB table
        clone_table(
            workflow.get_data_frame_table_name(),
            new_workflow.get_data_frame_table_name())

        # Clone actions
        for item_obj in workflow.actions.all():
            do_clone_action(user, item_obj, new_workflow)

        for item_obj in workflow.views.all():
            do_clone_view(user, item_obj, new_workflow)

        # Done!
        new_workflow.save()
    except Exception as exc:
        raise OnTaskServiceException(
            message=_('Error while cloning workflow: {0}').format(exc),
            to_delete=[new_workflow])

    workflow.log(
        user,
        models.Log.WORKFLOW_CLONE,
        id_old=workflow.id,
        name_old=workflow.name)

    return new_workflow
