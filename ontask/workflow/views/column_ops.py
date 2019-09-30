# -*- coding: utf-8 -*-

"""Views to move coumns and restrict values."""

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from ontask.core.decorators import ajax_required, get_column, get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.pandas import load_table
from ontask.models import Column, Log, Workflow
from ontask.workflow.ops import workflow_restrict_column


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@get_workflow(pf_related='columns')
def column_move(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Move a column using two names: from_name and to_name (POST params).

    The changes are reflected in the DB

    :param request:
    :return: AJAX response, empty.
    """
    from_name = request.POST.get('from_name')
    to_name = request.POST.get('to_name')
    if not from_name or not to_name:
        # Incorrect parameter
        return JsonResponse({})

    from_col = workflow.columns.filter(name=from_name).first()
    to_col = workflow.columns.filter(name=to_name).first()

    if not from_col or not to_col:
        # Incorrect condition name
        return JsonResponse({})

    # Two correct condition names, perform the swap
    from_col.reposition_and_update_df(to_col.position)

    return JsonResponse({})


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def column_move_top(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Move column to the first position.

    :param request: HTTP request to move a column to the top of the list

    :param pk: Column ID

    :return: Once done, redirects to the column page
    """
    # The workflow and column objects have been correctly obtained
    if column.position > 1:
        column.reposition_and_update_df(1)

    return redirect('workflow:detail')


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def column_move_bottom(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Move column to the last position.

    :param request: HTTP request to move a column to end of the list

    :param pk: Column ID

    :return: Once done, redirects to the column page
    """
    # The workflow and column objects have been correctly obtained
    if column.position < workflow.ncols:
        column.reposition_and_update_df(workflow.ncols)

    return redirect('workflow:detail')


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def column_restrict_values(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
    """Restrict future values in this column to one of those already present.

    :param request: HTTP request

    :param pk: ID of the column to restrict. The workflow element is taken
     from the session.

    :return: Render the delete column form
    """
    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    if column.is_key:
        # This is the only key column
        messages.error(request, _('You cannot restrict a key column'))
        return JsonResponse({'html_redirect': reverse('workflow:detail')})

    # Get the name of the column to delete
    context = {'pk': pk, 'cname': column.name}

    # Get the values from the data frame
    df = load_table(workflow.get_data_frame_table_name())
    context['values'] = ', '.join(set(df[column.name]))

    if request.method == 'POST':
        # Proceed restricting the column
        error_txt = workflow_restrict_column(column)

        if isinstance(error_txt, str):
            # Something went wrong. Show it
            messages.error(request, error_txt)

        column.log(request.user, Log.COLUMN_RESTRICT)
        return JsonResponse({'html_redirect': reverse('workflow:detail')})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_column_restrict.html',
            context,
            request=request),
    })
