# -*- coding: utf-8 -*-

"""Views to manipulate the workflow."""

from builtins import range
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from dataops.pandas import check_wf_df, load_table, store_dataframe
from logs.models import Log
from ontask import create_new_name
from ontask.celery import celery_is_up
from ontask.decorators import access_workflow, get_workflow
from ontask.permissions import UserIsInstructor, is_instructor
from workflow.forms import WorkflowForm
from workflow.models import Workflow
from workflow.ops import store_workflow_in_session


class WorkflowCreateView(UserIsInstructor, generic.TemplateView):
    """View to create a workflow."""

    form_class = WorkflowForm

    template_name = 'workflow/includes/partial_workflow_create.html'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        return context

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

    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """Process the post request."""
        return save_workflow_form(
            request,
            self.form_class(request.POST, workflow_user=request.user),
            self.template_name)


class WorkflowDetailView(UserIsInstructor, generic.DetailView):
    """Class to provide the detailed view of a single workflow.

    @DynamicAttrs
    """

    model = Workflow

    template_name = 'workflow/detail.html'

    context_object_name = 'workflow'

    def get_object(self, queryset=None):
        """Get the current object."""
        old_obj = super().get_object(queryset=queryset)

        # Check if the workflow is locked
        workflow = access_workflow(
            self.request,
            old_obj.id,
            prefetch_related=['actions', 'columns'])

        return workflow

    def get_context_data(self, **kwargs):
        """Get the context data to render the detailed page."""
        context = super().get_context_data(**kwargs)

        # Get the table information (if it exist)
        context['table_info'] = None
        if self.object.has_table():
            context['table_info'] = {
                'num_rows': self.object.nrows,
                'num_cols': self.object.ncols,
                'num_actions': self.object.actions.count(),
                'num_attributes': len(self.object.attributes)}

        # put the number of key columns in the context
        context['num_key_columns'] = self.object.columns.filter(
            is_key=True,
        ).count()

        # Guarantee that column position is set for backward compatibility
        columns = self.object.columns.all()
        if any(col.position == 0 for col in columns):
            # At least a column has index equal to zero, so reset all of them
            for idx, col in enumerate(columns):
                col.position = idx + 1
                col.save()

        # Safety check for consistency (only in development)
        if settings.DEBUG:
            check_wf_df(self.object)

            # Columns are properly numbered
            cpos = self.object.columns.all().values_list('position', flat=True)
            rng = range(1, len(cpos) + 1)
            assert sorted(cpos) == list(rng)

        return context


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
def index(request):
    """Render the page with the list of workflows."""
    wid = request.session.pop('ontask_workflow_id', None)
    # If removing workflow from session, mark it as available for sharing
    if wid:
        Workflow.unlock_workflow_by_id(wid)
    request.session.pop('ontask_workflow_name', None)

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
    form = WorkflowForm(request.POST or None,
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
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name})

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
@get_workflow()
def clone(
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

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + workflow.name
    while Workflow.objects.filter(name=new_name).exists():
        new_name = 'Copy of ' + new_name

    workflow.id = None
    workflow.name = create_new_name(
        workflow.name,
        Workflow.objects.filter(
            Q(workflow__user=request.user) | Q(workflow__shared=request.user),
        ),
    )

    try:
        workflow.save()
    except IntegrityError:
        messages.error(request, _('Unable to clone workflow'))
        return JsonResponse({'html_redirect': ''})

    # Get the initial object back
    workflow_new = workflow
    workflow = access_workflow(request, wid, prefetch_related='actions')

    # Clone the data frame
    data_frame = load_table(workflow.get_data_frame_table_name())
    store_dataframe(data_frame, workflow_new)

    # Clone actions
    for action in workflow.actions.all():
        action.ops.clone_action(action, workflow_new)

    # Done!
    workflow_new.save()

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
