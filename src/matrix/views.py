# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from dataops import ops
from dataops import pandas_db
from ontask.permissions import is_instructor
from workflow.ops import get_workflow


@user_passes_test(is_instructor)
def display(request):
    # TODO: https://editor.datatables.net/examples/inline-editing/simple
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_matrix(workflow.id):
        return render(request,
                      'matrix/display.html',
                      {})

    # Create the context with the column names
    context = {'column_names': ['Ops'] + workflow.get_column_names()}

    return render(request, 'matrix/display.html', context)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def display_ss(request):
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'error': 'Incorrect request. Unable to process'})

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_matrix(workflow.id):
        return JsonResponse({'error': 'There is no data in the matrix'})

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        order_col = request.POST.get('order[0][column]', None)
        order_dir = request.POST.get('order[0][dir]', 'asc')
    except ValueError:
        return JsonResponse({'error': 'Incorrect request. Unable to process'})

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get columns and names
    columns = workflow.columns.all()
    column_names = [x.name for x in columns]

    # See if an order has been given.
    if order_col:
        order_col = column_names[int(order_col) - 1]  # The first column is ops

    # Find the first key column
    key_name, key_idx = next(((c.name, idx) for idx, c in enumerate(columns)
                              if c.is_key), None)

    # Get the query set
    cv_tuples = []
    if search_value:
        cv_tuples = [(c.name, search_value, c.data_type) for c in columns]

    qs = pandas_db.search_table_rows(
        workflow.id,
        cv_tuples,
        True,
        order_col,
        order_dir == 'asc')[start:]

    # Post processing + adding operation columns and performing the search
    final_qs = []
    for row in qs:
        if search_value and not any([search_value in str(x) for x in row]):
            # If a search value is given, check if it is part of the row,
            # if not skip.
            continue

        ops_string = render_to_string(
            'matrix/includes/partial_matrix_ops.html',
            {'edit_url':
             reverse('dataops:rowupdate') +
             '?update_key={0}&update_val={1}'.format(key_name,
                                                     row[key_idx]),
             'delete_key': '?key={0}&value={1}'.format(key_name, row[key_idx]),
             }
        )
        final_qs.append(OrderedDict([('Ops', ops_string)] +
                                    list(zip(column_names, row))))
        if len(final_qs) == length:
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
def row_delete(request):
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
        # The response will require going to the matrix display anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('matrix:display')

        # if there is no key or value, flag the message and return to matrix
        # view
        if not key or not value:
            messages.error(request,
                           'Incorrect URL invoked to delete a row')
            return JsonResponse(data)

        # Proceed to delete the row
        pandas_db.delete_table_row_by_key(workflow.id, (key, value))

        # Update rowcount
        workflow.nrows -= 1
        workflow.save()

        return JsonResponse(data)

    # Render the page
    data['html_form'] = render_to_string(
        'matrix/includes/partial_row_delete.html',
        {'delete_key': '?key={0}&value={1}'.format(key, value)},
        request=request
    )

    return JsonResponse(data)
