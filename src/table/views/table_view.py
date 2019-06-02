# -*- coding: utf-8 -*-

"""Functions to implement CRUD views for Views."""
import copy
from typing import Optional

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dataops.formula import get_variables
from logs.models import Log
from ontask import create_new_name
from ontask.decorators import ajax_required, get_view, get_workflow
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from table.forms import ViewAddForm
from table.models import View
from workflow.models import Workflow


class ViewTable(tables.Table):
    """Table to display the set of views handled in a workflow."""

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(
        empty_values=[],
        verbose_name=_('Description'))

    operations = OperationsColumn(
        verbose_name='',
        template_file='table/includes/partial_view_operations.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render the name of the action as a link."""
        return format_html(
            """<a href="#" class="js-view-edit"
                  data-toggle="tooltip" data-url="{0}"
                  title="{1}">{2}</a>""",
            reverse('table:view_edit', kwargs={'pk': record['id']}),
            _('Change the columns present in the view'),
            record['name'],
        )

    class Meta(object):
        """Select the model and specify fields, sequence and attributes."""

        model = View

        fields = ('name', 'description_text', 'operations')

        sequence = ('name', 'description_text', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'view-table',
        }


def do_clone_view(
    view: View,
    new_workflow: Workflow = None,
    new_name: str = None,
) -> View:
    """Clone a view.

    :param view: Object to clone

    :param new_workflow: Non empty if it has to point to a new workflow

    :param new_name: Non empty if it has to be renamed.

    :result: New clone object
    """
    # Proceed to clone the view
    if new_name is None:
        new_name = view.name
    if new_workflow is None:
        new_workflow = view.workflow

    new_view = View(
        name=new_name,
        description_text=view.description_text,
        workflow=new_workflow,
        formula=copy.deepcopy(view.formula),
    )
    new_view.save()

    try:
        # Update the many to many field.
        new_view.columns.set(list(view.columns.all()))
    except Exception as exc:
        new_view.delete()
        raise exc

    return new_view


@user_passes_test(is_instructor)
@get_workflow(pf_related='views')
def view_index(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the list of views attached to a workflow.

    :param request:

    :return: HTTP response with the table

    """
    # Get the views
    views = workflow.views.values(
        'id',
        'name',
        'description_text',
        'modified')

    # Build the table only if there is anything to show (prevent empty table)
    return render(
        request,
        'table/view_index.html',
        {
            'query_builder_ops': workflow.get_query_builder_ops_as_str(),
            'table': ViewTable(views, orderable=False),
        },
    )


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='columns')
def view_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Create a new view.

    :param request: Request object

    :return: AJAX response
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add a view to a workflow without data'))
        return JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = ViewAddForm(request.POST or None, workflow=workflow)

    return save_view_form(
        request,
        form,
        'table/includes/partial_view_add.html',
    )


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_edit(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> JsonResponse:
    """Edit the content of a view.

    :param request: Request object

    :param pk: Primary key of the view

    :return: AJAX Response
    """
    # Form to read/process data
    form = ViewAddForm(request.POST or None, instance=view, workflow=workflow)

    return save_view_form(
        request,
        form,
        'table/includes/partial_view_edit.html')


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_delete(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> JsonResponse:
    """Delete a view.

    AJAX processor for the delete view operation

    :param request: AJAX request

    :param pk: primary key of the view to delete

    :return: AJAX response to handle the form.
    """
    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.VIEW_DELETE,
            view.workflow,
            {
                'id': view.id,
                'name': view.name,
                'workflow_name': view.workflow.name,
                'workflow_id': view.workflow.id})

        # Perform the delete operation
        view.delete()

        # In this case, the form is valid anyway
        return JsonResponse({'html_redirect': reverse('table:view_index')})

    return JsonResponse({
        'html_form': render_to_string(
            'table/includes/partial_view_delete.html',
            {'view': view},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_view(pf_related='views')
def view_clone(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> JsonResponse:
    """Clone a view.

    :param request: HTTP request

    :param pk: ID of the view to clone. The workflow is taken from the session

    :return: AJAX response
    """
    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'table/includes/partial_view_clone.html',
                {'pk': pk, 'vname': view.name},
                request=request),
        })

    # POST REQUEST
    old_name = view.name
    view = do_clone_view(
        view,
        new_workflow=None,
        new_name=create_new_name(view.name, workflow.views)
    )
    # Proceed to clone the view

    # Log the event
    Log.objects.register(
        request.user,
        Log.VIEW_CLONE,
        workflow,
        {'id': workflow.id,
         'name': workflow.name,
         'old_view_name': old_name,
         'new_view_name': view.name})

    return JsonResponse({'html_redirect': ''})


def save_view_form(
    request: HttpRequest,
    form: ViewAddForm,
    template_name: str,
) -> JsonResponse:
    """Save the data attached to a view as provided in a form.

    :param request: HTTP request

    :param form: Form object with the collected information

    :param template_name: To render the response

    :return: AJAX Response
    """
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        # Correct POST submission
        view = form.save(commit=False)
        view.workflow = form.workflow

        # Type of event to be recorded (before object is saved and ID is set)
        if form.instance.id:
            event_type = Log.VIEW_EDIT
        else:
            event_type = Log.VIEW_CREATE

        view.save()
        form.save_m2m()  # Needed to propagate the save effect to M2M relations

        # Log the event
        Log.objects.register(
            request.user,
            event_type,
            view.workflow,
            {
                'id': view.id,
                'name': view.name,
                'workflow_name': view.workflow.name,
                'workflow_id': view.workflow.id})

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id},
            request=request),
    })
