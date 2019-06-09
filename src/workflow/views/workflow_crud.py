# -*- coding: utf-8 -*-

"""Views to manipulate the workflow."""

import copy
from builtins import range
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from action.views.clone import do_clone_action
from dataops.pandas import check_wf_df
from dataops.sql import clone_table
from logs.models import Log
from ontask import create_new_name
from ontask.celery import celery_is_up
from ontask.decorators import ajax_required, get_workflow
from ontask.permissions import UserIsInstructor, is_instructor
from ontask.workflow_access import (
    remove_workflow_from_session, store_workflow_in_session,
)
from table.views.table_view import do_clone_view
from workflow.forms import WorkflowForm
from workflow.models import Workflow
from workflow.ops import do_clone_column_only


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    """View to create a workflow."""

    form_class = WorkflowForm

    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(ajax_required)
    def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> JsonResponse:
        """Process the get request."""
        return save_workflow_form(
            request,
            self.form_class(workflow_user=request.user),
            self.template_name)

    @method_decorator(ajax_required)
    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> JsonResponse:
        """Process the post request."""
        return save_workflow_form(
            request,
            self.form_class(request.POST, workflow_user=request.user),
            self.template_name)


def _do_clone_workflow(workflow: Workflow) -> Workflow:
    """Clone the workflow.

    :param workflow: source workflow

    :return: Clone object
    """
    new_workflow = Workflow(
        user=workflow.user,
        name=create_new_name(
            workflow.name,
            Workflow.objects.filter(
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
            do_clone_action(item_obj, new_workflow)

        for item_obj in workflow.views.all():
            do_clone_view(item_obj, new_workflow)

        # Done!
        new_workflow.save()
    except Exception as exc:
        new_workflow.delete()
        raise exc

    return new_workflow


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'shared'])
def detail(
    request: HttpRequest,
    workflow: Optional[Workflow],
) -> HttpResponse:
    """Http request to serve the details page for the workflow.

    :param request: HTTP Request

    :return:
    """
    context = {}
    # Get the table information (if it exist)
    context['workflow'] = workflow
    context['table_info'] = None
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

    # Safety check for consistency (only in development)
    if settings.DEBUG:
        check_wf_df(workflow)

        # Columns are properly numbered
        cpos = workflow.columns.all().values_list('position', flat=True)
        rng = range(1, len(cpos) + 1)
        assert sorted(cpos) == list(rng)

    return render(request, 'workflow/detail.html', context)


def save_workflow_form(
    request: HttpRequest,
    form,
    template_name: str,
) -> JsonResponse:
    """Save the workflow to create a form.

    :param request:

    :param form:

    :param template_name:

    :return:
    """
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        if form.instance.id:
            log_type = Log.WORKFLOW_UPDATE
            redirect_url = ''
            # Save the instance
            workflow_item = form.save()
        else:
            # This is a new instance!
            form.instance.user = request.user
            form.instance.nrows = 0
            form.instance.ncols = 0
            log_type = Log.WORKFLOW_CREATE
            redirect_url = reverse('dataops:uploadmerge')

            # Save the instance
            workflow_item = form.save()
            store_workflow_in_session(request, workflow_item)

        # Log event
        Log.objects.register(
            request.user,
            log_type,
            workflow_item,
            {'id': workflow_item.id, 'name': workflow_item.name})

        # Here we can say that the form processing is done.
        return JsonResponse({'html_redirect': redirect_url})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
def index(request: HttpRequest) -> HttpResponse:
    """Render the page with the list of workflows."""
    remove_workflow_from_session(request)

    workflows = (
        request.user.workflows_owner.all()
        | request.user.workflows_shared.all()
    )
    workflows = workflows.distinct()

    # We include the table only if it is not empty.
    context = {
        'workflows': workflows.order_by('name'),
        'nwflows': len(workflows),
    }

    # Report if Celery is not running properly
    if request.user.is_superuser:
        # Verify that celery is running!
        if not celery_is_up():
            messages.error(
                request,
                _(
                    'WARNING: Celery is not currently running. '
                    + 'Please configure it correctly.',
                ),
            )

    return render(request, 'workflow/index.html', context)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def update(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Update the workflow information (name, description).

    :param request: Request object

    :param pk: Workflow ID

    :return: JSON response
    """
    form = WorkflowForm(
        request.POST or None,
        instance=workflow,
        workflow_user=workflow.user)

    # If the user owns the workflow, proceed
    if workflow.user == request.user:
        return save_workflow_form(
            request,
            form,
            'workflow/includes/partial_workflow_update.html')

    # If the user does not own the workflow, notify error and go back to
    # index
    messages.error(
        request,
        _('You can only rename workflows you created.'))
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def delete(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Delete a workflow."""
    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.WORKFLOW_DELETE,
            None,
            {
                'id': workflow.id,
                'name': workflow.name})

        # Nuke the logs pointing to the workflow
        for litem in workflow.logs.all():
            litem.workflow = None
            litem.save()

        # Perform the delete operation
        workflow.delete()

        # In this case, the form is valid anyway
        return JsonResponse({'html_redirect': reverse('home')})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_delete.html',
            {'workflow': workflow},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def clone_workflow(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Clone a workflow.

    :param request: HTTP request

    :param pk: Workflow id

    :return: JSON data
    """
    # Get the current workflow
    # Initial data in the context
    context = {'pk': wid, 'name': workflow.name}

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_workflow_clone.html',
                context,
                request=request),
        })

    try:
        workflow_new = _do_clone_workflow(workflow)
    except Exception as exc:
        messages.error(
            request,
            _('Unable to clone workflow: {0}').format(str(exc)),
        )
        return JsonResponse({'html_redirect': ''})

    # Log event
    Log.objects.register(
        request.user,
        Log.WORKFLOW_CLONE,
        workflow_new,
        {
            'id_old': workflow_new.id,
            'id_new': workflow.id,
            'name_old': workflow_new.name,
            'name_new': workflow.name})

    messages.success(
        request,
        _('Workflow successfully cloned.'))
    return JsonResponse({'html_redirect': ''})
