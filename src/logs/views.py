# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

import pytz
from django.conf import settings as ontask_settings
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from .models import Log
from .ops import log_types


@user_passes_test(is_instructor)
def show(request):
    # Try to get workflow and if not present, go to home page
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Create the context with the column names
    context = {
        'workflow': workflow,
        'column_names': [_('ID'), _('Date/Time'), _('User'), _('Event type'), _('View')]
    }

    # Render the page with the table
    return render(request, 'logs/show.html', context)


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def show_ss(request):
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
    qs = Log.objects.filter(
        workflow__id=workflow.id
    )
    recordsTotal = qs.count()

    if search_value:
        # Refine the log
        qs = qs.filter(
            Q(id=search_value) |
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
            item[0],
            item[1].astimezone(pytz.timezone(ontask_settings.TIME_ZONE)),
            item[2],
            item[3],
            """<button type="submit" class="btn btn-primary btn-sm js-log-view"
                    data-url="{0}"
                    data-toggle="tooltip" title="{1}">
              <span class="glyphicon glyphicon-eye-open"></span> {2}
            </button>
            """.format(reverse('logs:view', kwargs={'pk': item[0]}),
                       _('View the content of this log'),
                       _('View'))]

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
def view_log_list(request, pk):
    # Get the log item
    log_item = Log.objects.get(pk=pk)
    data = dict()

    context = log_item.get_payload()

    # Add the name of the object, the workflow and the type
    context['log_type'] = log_item.name
    context['op_name'] = log_types[log_item.name]
    context['workflow'] = log_item.workflow

    # TODO: Change the model to include directly a JSON object, not this.
    context['json_pretty'] = json.dumps(json.loads(log_item.payload),
                                        sort_keys=True,
                                        indent=4)

    # Render the template and return as JSON response
    data['html_form'] = render_to_string(
        'logs/includes/partial_log_view.html',
        context,
        request=request)

    return JsonResponse(data)
