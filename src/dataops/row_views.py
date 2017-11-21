# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import generic
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse


from ontask.permissions import is_instructor, UserIsInstructor
from workflow.ops import get_workflow
from .forms import RowViewForm
from .models import RowView

field_prefix = '___ontask___upload_'


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
                reverse('dataops:rowview_edit', kwargs={'pk': record.id}),
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
        # It is a post so
        selected = [request.POST.get(field_prefix + '%s' % idx) is not None
                    for idx in range(len(columns))]
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

# class RowViewCreate(UserIsInstructor, generic.CreateView):
#     model = RowView
#     template_name = 'dataops/rowview_form.html'
#     form_class = RowViewForm
#
#     def get_context_data(self, **kwargs):
#
#         selected = [self.request.POST.get(field_prefix + '%s' % idx) is not None
#                     for idx in range(len(self.workflow.columns.all()))]
#
#         return {'col_info':
#                     create_column_info(self.request,
#                                        self.workflow,
#                                        selected),
#                 'form': self.get_form(),
#                 'field_prefix': field_prefix}
#
#     def get(self, request, *args, **kwargs):
#         """
#         Respond to the get request for the form to create a view
#         :param request: Contains the workflow being used
#         :param args: None
#         :param kwargs: None
#         :return: render the page
#         """
#
#         # Check if the workflow is locked
#         self.workflow = get_workflow(self.request)
#         if not self.workflow:
#             return redirect('workflow:index')
#
#         return render(self.request, self.template_name, self.get_context_data())
#
#     def post(self, request, *args, **kwargs):
#
#         # Check if the workflow is locked
#         self.workflow = get_workflow(self.request)
#         if not self.workflow:
#             return redirect('workflow:index')
#
#         # Bind the form and access the data field and the context
#         form = RowViewForm(request.POST)
#         ctx = self.get_context_data()
#
#         if not form.is_valid():
#             return render(self.request, self.template_name, ctx)
#
#         # Valid POST request
#
#         # Step 1: Make sure the name is correct
#         if RowView.objects.filter(name=request.POST.get('name')).exists():
#             form.add_error(
#                 'name',
#                 'There is already a view with this name'
#             )
#             ctx['form'] = form
#             return render(self.request, self.template_name, ctx)
#
#         # Get the information about the selected columns
#         columns = self.workflow.columns.all()
#         selection = [c for idx, c in enumerate(columns)
#                      if request.POST.get((self.field_prefix + '%s') % idx)]
#
#         # Step 2: Make sure there is at least a unique column
#         if not selection:
#             form.add_error(
#                 None,
#                 'There must be at least one unique column in the view'
#             )
#             ctx['form'] = form
#             return render(self.request, self.template_name, ctx)
#
#         # Step 3: There must be at least on key column
#         if not next((x for x in selection if x.is_key), None):
#             form.add_error(
#                 None,
#                 'There must be at least one unique column in the view'
#             )
#             ctx['form'] = form
#             return render(self.request, self.template_name, ctx)
#
#         # Save the element and populate the right columns
#         rowview = form.save(commit=False)
#         rowview.workflow = self.workflow
#         rowview.save()
#         for c in selection:
#             rowview.columns.add(c)
#         rowview.save()
#         return redirect(reverse('dataops:rowview_list'))
#
#
# class RowViewUpdate(UserIsInstructor, generic.UpdateView):
#     model = RowView
#     template_name = 'dataops/rowview_form.html'
#     form_class = RowViewForm
#
#     def get(self, request, *args, **kwargs):
#         """
#         Respond to the get request for the form to create a view
#         :param request: Contains the workflow being used
#         :param args: None
#         :param kwargs: None
#         :return: render the page
#         """
#
#         # Check if the workflow is locked
#         self.workflow = get_workflow(self.request)
#         if not self.workflow:
#             return redirect('workflow:index')
#
#         try:
#             rowview = RowView.objects.get(pk=kwargs['pk'])
#         except ObjectDoesNotExist:
#             return redirect('workflow:index')
#
#         form = RowViewForm(None, instance=rowview)
#
#         selected = [x in rowview.columns.all()
#                     for x in self.workflow.columns.all()]
#
#         return render(self.request,
#                       self.template_name,
#                       {'col_info': create_column_info(self.request,
#                                                       self.workflow,
#                                                       selected),
#                        'form': form,
#                        'field_prefix': field_prefix})
#
#     def post(self, request, *args, **kwargs):
#         # Check if the workflow is locked
#         self.workflow = get_workflow(self.request)
#         if not self.workflow:
#             return redirect('workflow:index')
#
#         try:
#             rowview = RowView.objects.get(pk=kwargs['pk'])
#         except ObjectDoesNotExist:
#             return redirect('workflow:index')
#
#         form = RowViewForm(None, instance=rowview)
#
#         selected = [x in rowview.columns.all()
#                     for x in self.workflow.columns.all()]
#
#
#
# class RowViewDelete(UserIsInstructor, generic.DeleteView):
#     model = RowView
#     success_url = reverse_lazy('dataops:rowview_list')
