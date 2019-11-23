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

from ontask import create_new_name
from ontask.action.views.clone import do_clone_action
from ontask.core.celery import celery_is_up
from ontask.core.decorators import ajax_required, get_workflow
from ontask.core.permissions import UserIsInstructor, is_instructor
from ontask.dataops.pandas import check_wf_df
from ontask.dataops.sql import clone_table
from ontask.models import Log, Workflow
from ontask.table.services.view import do_clone_view
from ontask.workflow.access import (
    remove_workflow_from_session, store_workflow_in_session,
)
from ontask.workflow.forms import WorkflowForm
from ontask.workflow.ops import do_clone_column_only


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    """View to create a workflow."""

    form_class = WorkflowForm
    template_name = 'workflow/includes/partial_workflow_create.html'

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
        cpos = workflow.columns.values_list('position', flat=True)
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
            workflow_item = form.save()
            workflow_item.nrows = 0
            workflow_item.ncols = 0
            log_type = Log.WORKFLOW_CREATE
            redirect_url = reverse('dataops:uploadmerge')

            # Store in session
            store_workflow_in_session(request, workflow_item)

        workflow_item.log(request.user, log_type)
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

    # Get the queryset for those with start and those without
    workflows_star = workflows.filter(star__in=[request.user])
    workflows_no_star = workflows.exclude(star__in=[request.user])

    # We include the table only if it is not empty.
    context = {
        'workflows_star': workflows_star.order_by('name'),
        'workflows': workflows_no_star.order_by('name'),
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
        workflow.log(request.user, Log.WORKFLOW_DELETE)
        workflow.delete()
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

    workflow.log(
        request.user,
        Log.WORKFLOW_CLONE,
        id_old=workflow.id,
        name_old=workflow.name)

    messages.success(
        request,
        _('Workflow successfully cloned.'))
    return JsonResponse({'html_redirect': ''})
