# -*- coding: utf-8 -*-
"""
File containing functions to implement all views related to the table element.
"""
from __future__ import unicode_literals, print_function

from datetime import datetime

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _

from dataops import ops, pandas_db
from logs.models import Log
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from workflow.ops import get_workflow
from .forms import ViewAddForm
from .models import View


class ViewTable(tables.Table):
    """
    Table to display the set of views handled in a workflow
    """
    name = tables.Column(verbose_name=_('Name'))
    description_text = tables.Column(
        empty_values=[],
        verbose_name=_('Description')
    )
    modified = tables.DateTimeColumn(verbose_name=_('Modified'))
    operations = OperationsColumn(
        verbose_name=_('Operations'),
        template_file='table/includes/partial_view_operations.html',
        template_context=lambda record: {'id': record['id']}
    )

    class Meta:
        """
        Select the model and specify fields, sequence and attributes
        """
        model = View
        fields = ('name', 'description_text', 'modified', 'operations')
        sequence = ('name', 'description_text', 'modified', 'operations')
        attrs = {
            'class': 'table display table-bordered',
            'id': 'view-table'
        }


def save_view_form(request, form, template_name):
    """
    Save the data attached to a view as provided in a form.
    :param request: HTTP request
    :param form: Form object with the collected information
    :param template_name: To render the response
    :return: AJAX Response
    """

    # Ajax response. Form is not valid until proven otherwise
    data = {'form_is_valid': False}

    # Type of event to be recorded
    if form.instance.id:
        event_type = Log.VIEW_EDIT
    else:
        event_type = Log.VIEW_CREATE

    # If a GET or incorrect request, render the form again
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id},
            request=request
        )
        return JsonResponse(data)

    # Correct POST submission
    view = form.save(commit=False)
    view.workflow = form.workflow

    # Save the new vew
    try:
        view.save()
        form.save_m2m()  # Needed to propagate the save effect to M2M relations
    except IntegrityError:
        form.add_error('name',
                       _('A view with that name already exists'))
        data['html_form'] = render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id},
            request=request
        )
        return JsonResponse(data)

    # Log the event
    Log.objects.register(request.user,
                         event_type,
                         view.workflow,
                         {'id': view.id,
                          'name': view.name,
                          'workflow_name': view.workflow.name,
                          'workflow_id': view.workflow.id})

    data['form_is_valid'] = True
    data['html_redirect'] = ''  # Refresh the page
    return JsonResponse(data)


def render_table_display_page(request, workflow, view, columns, ajax_url):
    """
    Function to render the content of the display page taking into account
    the columns to show and the AJAX url to use to render the table content.
    :param request: HTTP request
    :param workflow: Workflow object used to access the data frame
    :param view: View to use to render the table (or None)
    :param columns: Columns to display in the page
    :param ajax_url: URL to invoke to populate the table
    :return: HTTP Response
    """
    # Create the initial context
    context = {
        'query_builder_ops': workflow.get_query_builder_ops_as_str(),
        'ajax_url': ajax_url,
        'views': workflow.views.all(),
        'no_actions': workflow.actions.count() == 0
    }

    # If there is a DF, add the columns
    if ops.workflow_id_has_table(workflow.id):
        context['columns'] = columns

    # If using a view, add it to the context
    if view:
        context['view'] = view

    return render(request, 'table/display.html', context)


def render_table_display_data(request, workflow, columns, formula,
                              view_id=None):
    """
    Render the appropriate subset of the data table. Use the search string
     provided in the UI + the filter (if applicable) taken from a view.
    :param request: AJAX request
    :param workflow: workflow object
    :param columns: Subset of columns to consider
    :param formula: Expression to filter rows
    :param view_id: ID of the view restricting the display (if any)
    :return:
    """

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        order_col_name = request.POST.get('order[0][column]', None)
        order_dir = request.POST.get('order[0][dir]', 'asc')
    except ValueError:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get columns and names
    column_names = [x.name for x in columns]

    # See if an order has been given.
    if order_col_name:
        # The first column is ops
        order_col_name = column_names[int(order_col_name) - 1]

    # Find the first key column
    key_name, key_idx = next(((c.name, idx) for idx, c in enumerate(columns)
                              if c.is_key), None)

    # Get the filters to apply when fetching the query set
    cv_tuples = []
    if search_value:
        cv_tuples.extend(
            [(c.name, search_value, c.data_type) for c in columns]
        )

    qs = pandas_db.search_table_rows(
        workflow.id,
        cv_tuples,
        True,
        order_col_name,
        order_dir == 'asc',
        column_names,
        formula
    )

    # Post processing + adding operation columns and performing the search
    final_qs = []
    items = 0  # For counting the number of elements in the result
    for row in qs[start:start + length]:
        items += 1
        if view_id:
            stat_url = reverse('table:stat_row_view', kwargs={'pk': view_id})
        else:
            stat_url = reverse('table:stat_row')

        ops_string = render_to_string(
            'table/includes/partial_table_ops.html',
            {'stat_url': stat_url +
                         '?key={0}&val={1}'.format(key_name, row[key_idx]),
             'edit_url': reverse('dataops:rowupdate') +
                         '?update_key={0}&update_val={1}'.format(key_name,
                                                                 row[key_idx]),
             'delete_key': '?key={0}&value={1}'.format(key_name,
                                                       row[key_idx]),
             'view_id': view_id}
        )

        # Element to add to the final queryset
        new_element = [ops_string] + list(row)

        # Tweak the date time format
        new_element = map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S %z')
        if isinstance(x, datetime) else x, new_element)

        # Create the list of elements to display and add it ot the final QS
        final_qs.append(new_element)

        if items == length:
            # We reached the number or requested elements, abandon.
            break

    # Result to return as Ajax response
    data = {
        'draw': draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(qs),
        'data': final_qs
    }

    return JsonResponse(data)


@user_passes_test(is_instructor)
def display(request):
    """
    Initial page to show the table
    :param request: HTTP request
    :return: Initial rendering of the page with the table skeleton
    """
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    return render_table_display_page(
        request,
        workflow,
        None,
        workflow.columns.all(),
        reverse('table:display_ss')
    )


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def display_ss(request):
    """
    AJAX function to provide a subset of the table for visualisation
    :param request: HTTP request from dataTables
    :return: AJAX response
    """
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': _('There is no data in the table')})

    return render_table_display_data(
        request,
        workflow,
        workflow.columns.all(),
        None
    )


@user_passes_test(is_instructor)
def display_view(request, pk):
    """
    Initial page to show the table using a VIEW
    :param request: HTTP request
    :param pk: PK of the view to use
    :return: Initial rendering of the page with the table skeleton
    """
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    try:
        view = View.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The view has not been found, so it must be due to a session expire
        return redirect('table:display')

    return render_table_display_page(
        request,
        workflow,
        view,
        view.columns.all(),
        reverse('table:display_view_ss', kwargs={'pk': view.id})
    )


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def display_view_ss(request, pk):
    """
    AJAX function to provide a subset of the table for visualisation. The
    subset is defined by the elements in a view
    :param request: HTTP request from dataTables
    :param pk: Primary key of the view to be used
    :return: AJAX response
    """

    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': _('There is no data in the table')})

    try:
        view = View.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The view has not been found, so it must be due to a session expire
        return JsonResponse({'error': _('Incorrect view reference')})

    return render_table_display_data(
        request,
        workflow,
        view.columns.all(),
        view.formula,
        view.id
    )


@user_passes_test(is_instructor)
def row_delete(request):
    """
    Handle the steps to delete a row in the table
    :param request: HTTP request
    :return: AJAX response
    """
    # We only accept ajax requests here
    if not request.is_ajax():
        return redirect('workflow:index')

    # Result to return
    data = {}

    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the key/value pair to delete
    key = request.GET.get('key', None)
    value = request.GET.get('value', None)

    # Process the confirmed response
    if request.method == 'POST':
        # The response will require going to the table display anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('table:display')

        # if there is no key or value, flag the message and return to table
        # view
        if not key or not value:
            messages.error(request,
                           _('Incorrect URL invoked to delete a row'))
            return JsonResponse(data)

        # Proceed to delete the row
        pandas_db.delete_table_row_by_key(workflow.id, (key, value))

        # Update rowcount
        workflow.nrows -= 1
        workflow.save()

        # Update the value of all the conditions in the actions
        for action in workflow.actions.all():
            action.update_n_rows_selected()

        return JsonResponse(data)

    # Render the page
    data['html_form'] = render_to_string(
        'table/includes/partial_row_delete.html',
        {'delete_key': '?key={0}&value={1}'.format(key, value)},
        request=request
    )

    return JsonResponse(data)


@user_passes_test(is_instructor)
def view_index(request):
    """
    Render the list of views attached to a workflow
    :param request:
    :return: HTTP response with the table
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the views
    views = View.objects.filter(
        workflow__id=workflow.id).values('id',
                                         'name',
                                         'description_text',
                                         'modified')

    # Context to render the template
    context = {
        'query_builder_ops': workflow.get_query_builder_ops_as_str()
    }

    # Build the table only if there is anything to show (prevent empty table)
    if views.count() > 0:
        context['table'] = ViewTable(views, orderable=False)

    return render(request, 'table/view_index.html', context)


@user_passes_test(is_instructor)
def view_add(request):
    """
    Create a new view by processing the GET/POST requests related to the form.
    :param request: Request object
    :return: AJAX response
    """
    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('workflow:index')}
        )

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add a view to a workflow without data'))
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': ''}
        )

    # Form to read/process data
    form = ViewAddForm(request.POST or None, workflow=workflow)

    return save_view_form(request,
                          form,
                          'table/includes/partial_view_add.html')


@user_passes_test(is_instructor)
def view_edit(request, pk):
    """
    Process the GET/POST for the form to edit the content of a view
    :param request: Request object
    :param pk: Primary key of the view
    :return: AJAX Response
    """
    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('workflow:index')}
        )

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add a view to a workflow without data'))
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': ''}
        )

    # Get the view
    try:
        view = View.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).distinct().prefetch_related('columns').get(pk=pk)
    except ObjectDoesNotExist:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('table:view_index')}
        )

    # Form to read/process data
    form = ViewAddForm(request.POST or None,
                       instance=view,
                       workflow=workflow)

    return save_view_form(request,
                          form,
                          'table/includes/partial_view_edit.html')


@user_passes_test(is_instructor)
def view_delete(request, pk):
    """
    AJAX processor for the delete view operation
    :param request: AJAX request
    :param pk: primary key of the view to delete
    :return: AJAX response to handle the form.
    """
    # Data to send as JSON response, in principle, assume form is not valid
    data = {'form_is_valid': False}

    # Get the appropriate action object
    try:
        view = View.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('table:view_index')
        return JsonResponse(data)

    if request.method == 'POST':
        # Log the event
        Log.objects.register(request.user,
                             Log.VIEW_DELETE,
                             view.workflow,
                             {'id': view.id,
                              'name': view.name,
                              'workflow_name': view.workflow.name,
                              'workflow_id': view.workflow.id})

        # Perform the delete operation
        view.delete()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('table:view_index')

        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'table/includes/partial_view_delete.html',
        {'view': view},
        request=request)
    return JsonResponse(data)


@user_passes_test(is_instructor)
def view_clone(request, pk):
    """
    AJAX handshake to clone a view attached to the table
    :param request: HTTP request
    :param pk: ID of the view to clone. The workflow is taken from the session
    :return: AJAX response
    """
    # Data to send as JSON response, in principle, assume form is not valid
    data = {'form_is_valid': False}

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    context = {'pk': pk}  # For rendering

    # Get the view
    try:
        view = View.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The view is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the view to clone
    context['vname'] = view.name

    if request.method == 'GET':
        data['html_form'] = render_to_string(
            'table/includes/partial_view_clone.html',
            context,
            request=request)

        return JsonResponse(data)

    # POST REQUEST

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy_of_' + view.name
    while View.objects.filter(name=new_name,
                              workflow=view.workflow).exists():
        new_name = 'Copy_of_' + new_name

    # Proceed to clone the view
    old_name = view.name
    view.id = None
    view.name = new_name
    view.save()

    # Clone the columns
    view.columns.clear()
    view.columns.add(*list(View.objects.get(pk=pk).columns.all()))

    # Log the event
    Log.objects.register(request.user,
                         Log.VIEW_CLONE,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'old_view_name': old_name,
                          'new_view_name': view.name})

    return JsonResponse({'form_is_valid': True, 'html_redirect': ''})


@user_passes_test(is_instructor)
def csvdownload(request, pk=None):
    """

    :param request: HTML request
    :param pk: If given, the PK of the view to subset the table
    :return: Return a CSV download of the data in the table
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Check if dataframe is present
    if not ops.workflow_id_has_table(workflow.id):
        # Go back to show the workflow detail
        return redirect(reverse('workflow:detail',
                                kwargs={'pk': workflow.id}))

    # Get the columns from the view (if given)
    view = None
    if pk:
        try:
            view = View.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().prefetch_related('columns').get(pk=pk)
        except ObjectDoesNotExist:
            # Go back to show the workflow detail
            return redirect(reverse('workflow:detail',
                                    kwargs={'pk': workflow.id}))

    # Fetch the data frame
    data_frame = pandas_db.get_subframe(
        workflow.id,
        view,
        [x.name for x in view.columns.all()] if view is not None else None)

    # Create the response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="ontask_table.csv"'

    # Dump the data frame as the content of the response object
    data_frame.to_csv(path_or_buf=response, sep=str(','), index=False)

    return response
