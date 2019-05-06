# -*- coding: utf-8 -*-


import json
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse, render
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.datatables import DataTablesServerSidePaging
from ontask import simplify_datetime_str
from ontask.decorators import access_workflow, get_workflow
from ontask.permissions import is_instructor
from workflow.models import Workflow
from .models import Log


@user_passes_test(is_instructor)
@get_workflow()
def display(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    # Try to get workflow and if not present, go to home page
    # Create the context with the column names
    context = {
        'workflow': workflow,
        'column_names': [_('ID'), _('Date/Time'), _('User'), _('Event type')]
    }

    # Render the page with the table
    return render(request, 'logs/display.html', context)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
@get_workflow(pf_related='logs')
def display_ss(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    # Try to get workflow and if not present, go to home page
    # Check that the GET parameter are correctly given
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get the logs
    qs = workflow.logs
    recordsTotal = qs.count()

    if dt_page.search_value:
        # Refine the log
        qs = qs.filter(
            Q(id__icontains=dt_page.search_value) |
            Q(user__email__icontains=dt_page.search_value) |
            Q(name__icontains=dt_page.search_value) |
            Q(payload__icontains=dt_page.search_value),
            workflow__id=workflow.id,
        ).distinct()

    # Order and select values
    qs = qs.order_by(F('created').desc()).values_list(
        'id', 'created', 'user__email', 'name'
    )
    recordsFiltered = qs.count()

    final_qs = []
    for item in qs[dt_page.start:dt_page.start + dt_page.length]:
        row = [
            """<a href="{0}" class="spin"
                  data-toggle="tooltip" title="{1}">{2}</a>""".format(
                reverse('logs:view', kwargs={'pk': item[0]}),
                ugettext('View log content'),
                item[0]
            ),
            simplify_datetime_str(item[1]),
            item[2],
            item[3],
        ]

        # Add the row to the final query_set
        final_qs.append(row)

    # Result to return as AJAX response
    data = {
        'draw': dt_page.draw,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'data': final_qs
    }
    # Render the page with the table
    return JsonResponse(data)


@user_passes_test(is_instructor)
@get_workflow()
def view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """View the content of one of the logs.

    :param request:

    :param pk:

    :return:
    """
    # Get the log item
    log_item = Log.objects.filter(
        pk=pk,
        user=request.user,
        workflow=workflow,
    ).first()

    # If the log item is not there, flag!
    if not log_item:
        messages.error(request, _('Incorrect log number requested'))
        return redirect(reverse('logs:index'))

    context = {'log_item': log_item}

    context['json_pretty'] = json.dumps(
        log_item.payload,
        sort_keys=True,
        indent=4)

    return render(request, 'logs/view.html', context)
