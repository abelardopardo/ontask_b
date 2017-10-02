# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
import django_tables2 as tables

from workflow.models import Workflow
from dataops import panda_db
from ontask import is_instructor, slugify
from .forms import RowFilterForm, RowUpdateForm

@login_required
@user_passes_test(is_instructor)
def dataops(request):
    workflow_id = request.session.get('ontask_workflow_id', None)
    if workflow_id is None:
        # Redirect to the workflow page to choose a workflow
        return redirect('workflow:index')

    # Get the workflow that is being used
    get_object_or_404(Workflow, pk=workflow_id)

    return render(request, 'dataops/data_ops.html')


@login_required
@user_passes_test(is_instructor)
def row_filter(request):
    workflow = get_object_or_404(
        Workflow,
        pk=request.session.get('ontask_workflow_id', -1),
        user=request.user)

    context = {}
    if workflow.nrows == 0:
        return render(request, 'dataops/row_filter.html', context)

    form = RowFilterForm(request.POST or None, workflow=workflow)
    context['form'] = form

    if request.method == 'POST':

        if form.is_valid():
            subquery = []
            fields = []
            for name, type in zip(form.key_names, form.key_types):
                # None or '', skip
                if not form.cleaned_data[name]:
                    continue

                subquery.append('{0} = %s'.format(name))
                fields.append(form.cleaned_data[name])

            if subquery:
                subquery = ' WHERE ' + ' AND '.join(subquery)
            else:
                subquery = None

            # Get the queryset from the matrix
            queryset = panda_db.execute_select_on_table(
                workflow.id,
                subquery,
                fields
            )

            # If the queryset returned a single element, create the row form
            # and return
            if len(queryset) == 1:
                row_form = RowUpdateForm(
                    workflow=workflow,
                    initial_values=list(queryset[0])
                )

                context['row_form'] = row_form
            else:
                # Add error in form and redisplay
                form.add_error(None, 'No data found with these values')

    return render(request, 'dataops/row_filter.html', context)


@login_required
@user_passes_test(is_instructor)
def row_update(request):
    """
    Receives a POST request to update a row in the data matrix
    :param request: Request object with all the data.
    :return:
    """
    pass


class RowTable(tables.Table):
    SID = tables.Column()