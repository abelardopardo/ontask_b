# -*- coding: utf-8 -*-


import json

import pytz
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse, render
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import simplify_datetime_str
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .models import Log


@user_passes_test(is_instructor)
def display(request):
    # Try to get workflow and if not present, go to home page
    workflow = get_workflow(request)
    if not workflow:
        return redirect('home')

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
def display_ss(request):
    # Try to get workflow and if not present, go to home page
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
    except ValueError:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get the logs
    qs = workflow.logs
    recordsTotal = qs.count()

    if search_value:
        # Refine the log
        qs = qs.filter(
            Q(id__icontains=search_value) |
            Q(user__email__icontains=search_value) |
            Q(name__icontains=search_value) |
            Q(payload__icontains=search_value),
            workflow__id=workflow.id,
        ).distinct()

    # Order and select values
    qs = qs.order_by(F('created').desc()).values_list(
        'id', 'created', 'user__email', 'name'
    )
    recordsFiltered = qs.count()

    final_qs = []
    for item in qs[start:start + length]:
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
        'draw': draw,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'data': final_qs
    }
    # Render the page with the table
    return JsonResponse(data)


@user_passes_test(is_instructor)
def view(request, pk):

    # Ajax response
    data = dict()
    data['form_is_valid'] = False

    # Try to get workflow and if not present, go to home page
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Get the log item
    log_item = Log.objects.filter(
        pk=pk,
        user=request.user,
        workflow=workflow
    ).first()

    # If the log item is not there, flag!
    if not log_item:
        messages.error(request, _('Incorrect log number requested'))
        return redirect(reverse('logs:index'))

    context = {'log_item': log_item}

    context['json_pretty'] = json.dumps(log_item.payload,
                                        sort_keys=True,
                                        indent=4)

    return render(request, 'logs/view.html', context)
