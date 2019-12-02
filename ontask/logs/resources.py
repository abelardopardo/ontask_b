# -*- coding: utf-8 -*-

"""View to export logs."""
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from import_export import resources

from ontask import models
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor


class LogResource(resources.ModelResource):
    """Model resource to handle logs."""

    class Meta:
        """Define model and fields."""

        model = models.Log
        fields = ('id', 'created', 'name', 'payload',)


@user_passes_test(is_instructor)
@get_workflow()
def export(request, wid):
    """Export the logs from the given workflow

    :param request: HTML request
    :param wid: pk of the workflow to export
    :return: Return a CSV download of the logs
    """
    dataset = LogResource().export(
        models.Log.objects.filter(user=request.user, workflow__id=wid)
    )

    # Create the response as a csv download
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs.csv"'

    return response
