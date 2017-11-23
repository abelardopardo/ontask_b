# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import generic

import logs.ops
from dataops.forms import field_prefix
from ontask.permissions import is_instructor, UserIsInstructor
from workflow.ops import get_workflow
from . import pandas_db
from .forms import RowViewForm, RowViewDataSearchForm, RowViewDataEntryForm
from .models import RowView


class OperationsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        self.template_file = kwargs.pop('template_file')
        super(OperationsColumn, self).__init__(*args, **kwargs)
        self.attrs = {'td': {'class': 'dt-body-center'}}

    def render(self, record, table):
        return render_to_string(self.template_file, {'id': record.id})


class RowViewTable(tables.Table):
    """
    Table to show the actions
    """

    name = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Name')
    )

    description_text = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Description')
    )

    modified = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Modified'

    )

    columns = OperationsColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Operations',
        template_file='dataops/includes/partial_rowview_operations.html'
    )

    def render_name(self, record):
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('dataops:rowview_dataentry',
                        kwargs={'pk': record.id}),
                record.name
            )
        )

    class Meta:
        model = RowView

        fields = ('name', 'description_text', 'modified', 'columns')

        sequence = ('name', 'description_text', 'modified', 'columns')

        exclude = ('created')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'rowview-table'
        }

        row_attrs = {
            'style': 'text-align:center;'
        }


class RowViewList(UserIsInstructor, generic.ListView):
    """
    CBV to list the available Row Views. A Row View is simply a subset of
    columns to consider for data entry. This Class is used just to list the
    row views available for a given workflow.
    """
    model = RowView

    def get_queryset(self):
        qs = super(RowViewList, self).get_queryset()

        # Filter only those elements that are related to the current workflow

        # Check if the workflow is locked
        self.workflow = get_workflow(self.request)
        if not self.workflow:
            redirect('workflow:index')

        # Filter with the workflow
        return qs.filter(workflow=self.workflow)

    def get_context_data(self, **kwargs):
        """
        Function that simply creates the table and places it in the context
        :param kwargs:
        :return:
        """
        ctx = super(RowViewList, self).get_context_data()
        ctx['table'] = RowViewTable(self.object_list, orderable=False)
        return ctx


def save_rowview_data(request, rowview_id, template_name):
    """
    :param request: Http request with a GET or a POST request
    :param rowview_id: Id of a rowview object or None (new object)
    :param template_name: Template to apply for rendering
    :return: HttpResponse object
    """

    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.nrows == 0:
        messages.error(request,
                       'Workflow has no data. '
                       'Go to Dataops to upload data.')
        return redirect(reverse('dataops:rowview_list'))

    # Get the list of columns from the workflow
    columns = workflow.columns.all()

    # Get the instance if given
    rowview = None
    if rowview_id:
        try:
            rowview = RowView.objects.get(id=rowview_id,
                                          workflow=workflow)
        except ObjectDoesNotExist:
            return redirect('workflow:index')

    # Bind the form and access the data field and the context
    form = RowViewForm(request.POST or None, instance=rowview)

    # Create a list with either column name if selected or None
    if request.method == 'POST':
        selected = [None if request.POST.get(field_prefix + '%s' % idx) is None
                    else c for idx, c in enumerate(columns)]
    elif rowview_id:
        selected = [x if x in rowview.columns.all() else None for x in columns]
    else:
        selected = [None] * len(columns)

    # Create the context info. Col info is to render the table, field_prefix
    # is to name the fields in the form, and finally the form
    ctx = {'col_info': [(c.name,
                         c.data_type,
                         c.is_key,
                         selected[idx] is not None)
                        for idx, c in enumerate(columns)],
           'field_prefix': field_prefix,
           'query_builder_ops': workflow.get_query_builder_ops_as_str(),
           'form': form,
           }

    # If it is a GET, or an invalid POST, render the template again
    if request.method == 'GET' or not form.is_valid():
        return render(request, template_name, ctx)

    # Valid POST request

    # There must be at least a key and a non-key columns
    is_there_key = False
    is_there_nonkey = False
    for c in selected:
        if not c:
            # Skip the columns that have not been selected
            continue

        # Check for the two conditions
        if c.is_key:
            is_there_key = True
        else:
            is_there_nonkey = True

    # Step 1: Make sure there is at least a unique column
    if not is_there_key:
        form.add_error(
            None,
            'There must be at least one unique column in the view'
        )
        ctx['form'] = form
        return render(request, template_name, ctx)

    # Step 2: There must be at least on key column
    if not is_there_nonkey:
        form.add_error(
            None,
            'There must be at least one non-unique column in the view'
        )
        ctx['form'] = form
        return render(request, template_name, ctx)

    # Save the element and populate the right columns
    rowview = form.save(commit=False)
    if not rowview_id:
        # New element
        rowview.workflow = workflow
        try:
            rowview.save()
        except IntegrityError:
            form.add_error('name', 'There is a view already with this name')
            return render(request, template_name, ctx)

    # Update set of columns (flush first)
    rowview.columns.clear()
    for c in selected:
        if not c:
            # Skip the columns that have not been selected
            continue
        rowview.columns.add(c)
    rowview.save()

    # Finish processing
    return redirect(reverse('dataops:rowview_list'))


@user_passes_test(is_instructor)
def rowview_create(request):
    return save_rowview_data(request, None, 'dataops/rowview_form.html')


@user_passes_test(is_instructor)
def rowview_update(request, pk):
    return save_rowview_data(request, pk, 'dataops/rowview_form.html')


@user_passes_test(is_instructor)
def rowview_delete(request, pk):
    """
    Delete a row view
    :param request: Request object with a GET or POST
    :param pk: Unique identifier of the row view
    :return:
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the rowview
    try:
        rowview = RowView.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The rowview is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('dataops:rowview_list')
        return JsonResponse(data)

    if request.method == 'POST':
        # Proceed with the delete
        rowview.delete()

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('dataops:rowview_list')
        return JsonResponse(data)

    context['name'] = rowview.name
    data['html_form'] = render_to_string(
        'dataops/includes/partial_rowview_delete.html',
        context,
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def rowview_dataentry(request, pk):
    # Get the workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the rowview from the PK
    try:
        rowview = RowView.objects.get(pk=pk,
                                      workflow=workflow)
    except ObjectDoesNotExist:
        return redirect('dataops:rowview_list')
    columns = rowview.columns.all()

    # Add to context for rendering the title
    context = {'workflow': workflow,
               'cancel_url': reverse('dataops:rowview_list')}

    # If the workflow does not have any rows, there is no point on doing this.
    if workflow.nrows == 0:
        messages.error(request,
                       'Workflow has no data. '
                       'Go to Dataops to upload data.')
        return redirect(reverse('dataops:rowview_list'))

    form = RowViewDataSearchForm(data=request.POST or None, columns=columns)

    # This form is always rendered, so it is included in the context anyway
    context['form'] = form

    if request.method != 'POST':
        return render(request, 'dataops/row_filter.html', context)

    if request.POST.get('submit') == 'update':
        # This is the case in which the row is updated
        row_form = RowViewDataEntryForm(request.POST, columns=columns)
        if row_form.is_valid() and row_form.has_changed():
            # Update content in the DB
            set_fields = []
            set_values = []
            where_field = None
            where_value = None
            log_payload = []
            # Create the SET name = value part of the query
            for idx, column in enumerate(columns):
                value = row_form.cleaned_data[field_prefix + '%s' % idx]
                if column.is_key:
                    if not where_field:
                        # Remember one unique key for selecting the row
                        where_field = column.name
                        where_value = value
                    continue

                set_fields.append(column.name)
                set_values.append(value)
                log_payload.append((column.name, value))

            pandas_db.update_row(workflow.id,
                                 set_fields,
                                 set_values,
                                 [where_field],
                                 [where_value])

            # Log the event
            logs.ops.put(request.user,
                         'matrixrow_update',
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'new_values': log_payload})

            # Change is done.
    else:
        if form.is_valid():
            # Request is a POST of the SEARCH (first form)
            where_field = []
            where_value = []
            for idx, col in enumerate(form.key_cols):
                value = form.cleaned_data[field_prefix + '%s' % idx]
                if value:
                    # Remember the value of the key
                    where_field = col.name
                    where_value = value
                    break

            # Get the row from the matrix
            rows = pandas_db.execute_select_on_table(workflow.id,
                                                     [where_field],
                                                     [where_value])

            if len(rows) == 1:
                # A single row has been selected. Create and pre-populate
                # the update form
                vals = [rows[0][idx]
                        for idx, c in enumerate(workflow.columns.all())
                        if c in columns]
                row_form = RowViewDataEntryForm(None,
                                                columns=columns,
                                                initial_values=vals)
                context['row_form'] = row_form
            else:
                form.add_error(None, 'No data found with the given keys')

    return render(request, 'dataops/row_filter.html', context)
