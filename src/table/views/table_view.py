from typing import Optional

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dataops.pandas import get_subframe
from logs.models import Log
from ontask import create_new_name
from ontask.decorators import get_view, get_workflow
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from table.forms import ViewAddForm
from table.models import View
from workflow.models import Workflow


class ViewTable(tables.Table):
    """
    Table to display the set of views handled in a workflow
    """
    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(
        empty_values=[],
        verbose_name=_('Description')
    )
    operations = OperationsColumn(
        verbose_name='',
        template_file='table/includes/partial_view_operations.html',
        template_context=lambda record: {'id': record['id']}
    )

    def render_name(self, record):
        return format_html(
            """<a href="#" class="js-view-edit"
                  data-toggle="tooltip" data-url="{0}"
                  title="{1}">{2}</a>""",
            reverse('table:view_edit', kwargs={'pk': record['id']}),
            _('Change the columns present in the view'),
            record['name']
        )

    class Meta(object):
        """
        Select the model and specify fields, sequence and attributes
        """
        model = View
        fields = ('name', 'description_text', 'operations')
        sequence = ('name', 'description_text', 'operations')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'view-table'
        }


@user_passes_test(is_instructor)
@get_workflow(pf_related='views')
def view_index(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """
    Render the list of views attached to a workflow
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
@get_workflow(pf_related='columns')
def view_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create a new view by processing the GET/POST requests related to the form.

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
        'table/includes/partial_view_add.html'
    )


@user_passes_test(is_instructor)
@get_view(pf_related='views')
def view_edit(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """
    Process the GET/POST for the form to edit the content of a view
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
@get_workflow(pf_related='views')
def view_delete(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """
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
            request=request)
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='views')
def view_clone(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """AJAX handshake to clone a view attached to the table.

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

    # Proceed to clone the view
    old_name = view.name
    view.id = None
    view.name = create_new_name(view.name, workflow.views)
    view.save()

    # Clone the columns
    view.columns.clear()
    view.columns.add(*list(workflow.views.get(pk=pk).columns.all()))

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


@user_passes_test(is_instructor)
@get_view(pf_related=['columns', 'views'])
def csvdownload(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """

    :param request: HTML request
    :param pk: If given, the PK of the view to subset the table
    :return: Return a CSV download of the data in the table
    """
    # Fetch the data frame
    if view:
        col_names = [x.name for x in view.columns.all()]
        formula = view.formula
    else:
        col_names = workflow.get_column_names()
        formula = None
    data_frame = get_subframe(
        workflow.get_data_frame_table_name(),
        formula,
        col_names
    )

    # Create the response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="ontask_table.csv"'

    # Dump the data frame as the content of the response object
    data_frame.to_csv(path_or_buf=response,
                      sep=str(','),
                      index=False,
                      encoding='utf-8')

    return response


def save_view_form(request, form, template_name):
    """Save the data attached to a view as provided in a form.

    :param request: HTTP request

    :param form: Form object with the collected information

    :param template_name: To render the response

    :return: AJAX Response
    """
    if request.method == 'POST' and form.is_valid():
        # Correct POST submission
        view = form.save(commit=False)
        view.workflow = form.workflow

        # Type of event to be recorded
        if form.instance.id:
            event_type = Log.VIEW_EDIT
        else:
            event_type = Log.VIEW_CREATE

        # Save the new vew
        # TODO: Fix handling this in the form clean method!
        try:
            view.save()
            form.save_m2m()  # Needed to propagate the save effect to M2M relations
        except IntegrityError:
            form.add_error('name',
                           _('A view with that name already exists'))
            return JsonResponse({
                'html_form': render_to_string(
                    template_name,
                    {'form': form, 'id': form.instance.id},
                    request=request),
            })

        # Log the event
        Log.objects.register(request.user,
                             event_type,
                             view.workflow,
                             {'id': view.id,
                              'name': view.name,
                              'workflow_name': view.workflow.name,
                              'workflow_id': view.workflow.id})

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id},
            request=request)
    })
