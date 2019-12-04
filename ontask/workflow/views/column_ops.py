# -*- coding: utf-8 -*-

"""Views to move coumns and restrict values."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from ontask import OnTaskServiceException, models
from ontask.core import ajax_required, get_column, get_workflow, is_instructor
from ontask.dataops.pandas import load_table
from ontask.workflow import services


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@get_workflow(pf_related='columns')
def column_move(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Move a column using two names: from_name and to_name (POST params).

    The changes are reflected in the DB

    :param request:
    :param workflow: Workflow being manipulated
    :return: AJAX response, empty.
    """
    from_name = request.POST.get('from_name')
    to_name = request.POST.get('to_name')
    if not from_name or not to_name:
        return http.JsonResponse({})

    from_col = workflow.columns.filter(name=from_name).first()
    to_col = workflow.columns.filter(name=to_name).first()

    if not from_col or not to_col:
        return http.JsonResponse({})

    from_col.reposition_and_update_df(to_col.position)

    return http.JsonResponse({})


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def column_move_top(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.HttpResponse:
    """Move column to the first position.

    :param request: HTTP request to move a column to the top of the list
    :param pk: Column ID
    :param workflow: Workflow being manipulated
    :param column: Column pointed by the pk
    :return: Once done, redirects to the column page
    """
    del request, pk, workflow
    # The workflow and column objects have been correctly obtained
    if column.position > 1:
        column.reposition_and_update_df(1)

    return redirect('workflow:detail')


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def column_move_bottom(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.HttpResponse:
    """Move column to the last position.

    :param request: HTTP request to move a column to end of the list
    :param pk: Column ID
    :param workflow: Workflow being used
    :param column: Column pointed by the pk
    :return: Once done, redirects to the column page
    """
    del request, pk
    # The workflow and column objects have been correctly obtained
    if column.position < workflow.ncols:
        column.reposition_and_update_df(workflow.ncols)

    return redirect('workflow:detail')


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def column_restrict_values(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.JsonResponse:
    """Restrict future values in this column to one of those already present.

    :param request: HTTP request
    :param pk: ID of the column to restrict. The workflow element is taken
     from the session.
    :param workflow: Workflow being used
    :param column: Column pointed by the pk
    :return: Render the delete column form
    """
    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    if column.is_key:
        messages.error(request, _('You cannot restrict a key column'))
        return http.JsonResponse({'html_redirect': reverse('workflow:detail')})

    if request.method == 'POST':
        try:
            services.restrict_column(request.user, column)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)

        return http.JsonResponse({'html_redirect': reverse('workflow:detail')})

    df = load_table(workflow.get_data_frame_table_name())
    return http.JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_column_restrict.html',
            {
                'pk': pk,
                'cname': column.name,
                'values': ', '.join(set(df[column.name]))},
            request=request),
    })
