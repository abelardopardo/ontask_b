# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from import_export import resources

from .models import Log


class LogResource(resources.ModelResource):
    class Meta:
        model = Log
        fields = ('id', 'created', 'name', 'payload',)


def export(request, pk):
    """

    :param request: HTML request
    :param pk: pk of the workflow to export
    :return: Return a CSV download of the logs
    """

    # Create a log resource object
    log_resources = LogResource()

    # Select the dataset to dump
    logs = Log.objects.filter(
        user=request.user,
        workflow__id=request.session.get('ontask_workflow_id', -1)
    )

    if len(logs) == 0:
        # No records found!!
        pass

    dataset = log_resources.export(logs)

    # Create the response as a csv download
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="logs.csv"'

    return response
