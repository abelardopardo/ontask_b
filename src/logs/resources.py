# -*- coding: utf-8 -*-


from builtins import object
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from import_export import resources

from ontask.permissions import is_instructor
from .models import Log


class LogResource(resources.ModelResource):
    class Meta(object):
        model = Log
        fields = ('id', 'created', 'name', 'payload',)


@user_passes_test(is_instructor)
def export(request, pk):
    """

    :param request: HTML request
    :param pk: pk of the workflow to export
    :return: Return a CSV download of the logs
    """

    # Create a log resource object
    log_resources = LogResource()

    # Select the dataset to dump
    logs = Log.objects.filter(user=request.user, workflow__id=pk)

    if logs.count() == 0:
        # No records found!!
        pass

    dataset = log_resources.export(logs)

    # Create the response as a csv download
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="logs.csv"'

    return response
