# -*- coding: utf-8 -*-

"""Service functions to manipulate logs."""
from typing import Dict, Optional

from django import http
from django.db.models import F, Q
from django.shortcuts import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from import_export import resources

from ontask import models, simplify_datetime_str
from ontask.celery import get_task_logger
from ontask.core import DataTablesServerSidePaging

LOGGER = get_task_logger('celery_execution')


class LogResource(resources.ModelResource):
    """Model resource to handle logs."""

    class Meta:
        """Define model and fields."""

        model = models.Log
        fields = ('id', 'created', 'name', 'payload',)


def get_log_item(log_id: int) -> Optional[models.Log]:
    """Get the log object.

    Given a log_id, fetch it from the Logs table. This is the object used to
    write all the diagnostics.

    :param log_id: PK of the Log object to get
    :return:
    """
    log_item = models.Log.objects.filter(pk=log_id).first()
    if not log_item:
        # Not much can be done here. Call has no place to report error...
        LOGGER.error(
            ugettext('Incorrect execution request with log_id %s'),
            str(log_id))

    return log_item


def log_table_server_side(
    request: http.HttpRequest,
    workflow: models.Workflow
) -> Dict:
    """Create the server side response for the table of logs.

    :param request: Http Request
    :param workflow: Workflow being considered.
    :return:
    """
    dt_page = DataTablesServerSidePaging(request)
    if not dt_page.is_valid:
        return http.JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get the logs
    qs = workflow.logs
    records_total = qs.count()

    if dt_page.search_value:
        # Refine the log
        qs = qs.filter(
            Q(id__icontains=dt_page.search_value)
            | Q(user__email__icontains=dt_page.search_value)
            | Q(name__icontains=dt_page.search_value)
            | Q(payload__icontains=dt_page.search_value),
            workflow__id=workflow.id,
        ).distinct()

    # Order and select values
    qs = qs.order_by(F('created').desc()).values_list(
        'id',
        'name',
        'created',
        'user__email')
    records_filtered = qs.count()

    final_qs = []
    for log_item in qs[dt_page.start:dt_page.start + dt_page.length]:
        row = [
            '<button type="button" data-url="{0}"'.format(
                reverse('logs:view', kwargs={'pk': log_item[0]}),
            )
            + ' class="btn btn-sm btn-light js-log-view"'
            + ' data-toggle="tooltip" title="{0}">{1}</button>'.format(
                ugettext('View log content'),
                log_item[0],
            ),
            models.Log.LOG_TYPES[log_item[1]],
            simplify_datetime_str(log_item[2]),
            log_item[3],
        ]

        # Add the row to the final query_set
        final_qs.append(row)

    return {
        'draw': dt_page.draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': final_qs,
    }
