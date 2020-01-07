# -*- coding: utf-8 -*-

"""Views to flush, show details, column server side, etc."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import OnTaskServiceException, models
from ontask.core import (
    ajax_required, get_column, get_workflow,
    is_instructor)
from ontask.workflow import services


@user_passes_test(is_instructor)
@get_workflow(s_related='luser_email_column', pf_related=['columns', 'shared'])
def operations(
    request: HttpRequest,
    workflow: Optional[models.Workflow],
) -> HttpResponse:
    """Http request to serve the operations page for the workflow.

    :param request: HTTP Request
    :param workflow: Workflow being manipulated.
    :return: HttpResponse of the operations page.
    """
    # Check if lusers is active and if so, if it needs to be refreshed
    services.check_luser_email_column_outdated(workflow)

    return render(
        request,
        'workflow/operations.html',
        services.get_operations_context(workflow))


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def flush(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> JsonResponse:
    """Render the view to flush a workflow."""
    del wid
    if workflow.nrows == 0:
        # Table is empty, redirect to data upload
        return JsonResponse({'html_redirect': reverse('dataops:uploadmerge')})

    if request.method == 'POST':
        services.do_flush(request, workflow)
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_workflow_flush.html',
            {'workflow': workflow},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def star(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> JsonResponse:
    """Toggle the star mark in the workflow.

    :param request: Http request
    :param wid: Primary key of the workflow
    :param workflow: Workflow being manipulated.
    :return: Empty JSON, side effect start relation is updated.
    """
    del wid
    # Get the workflows with stars
    stars = request.user.workflows_star.all()
    if workflow in stars:
        workflow.star.remove(request.user)
    else:
        workflow.star.add(request.user)

    workflow.log(request.user, models.Log.WORKFLOW_STAR)
    return JsonResponse({})


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_column()
def assign_luser_column(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> JsonResponse:
    """Render the view to assign the luser column.

    AJAX view to assign the column with id PK to the field luser_email_column
    and calculate the hash

    :param request: HTTP request
    :param pk: Column id
    :param workflow: Workflow being manipulated.
    :param column: Column to assign as the LUSER value
    :return: JSON data to perform the operation
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _(
                'Workflow has no data. '
                + 'Go to "Manage table data" to upload data.'))
        return JsonResponse({'html_redirect': reverse('action:index')})

    try:
        services.update_luser_email_column(
            request.user,
            pk,
            workflow,
            column)
        messages.success(
            request,
            _('The list of workflow users will be updated shortly.'),
        )
    except OnTaskServiceException as exc:
        exc.message_to_error(request)

    return JsonResponse({'html_redirect': ''})
