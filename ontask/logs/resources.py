# -*- coding: utf-8 -*-

"""View to export logs."""

from builtins import object

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from import_export import resources

from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor

from ontask.models import Log


class LogResource(resources.ModelResource):
    """Model resource to handle logs."""

    class Meta(object):
        """Define model and fields."""

        model = Log

        fields = ('id', 'created', 'name', 'payload',)


@user_passes_test(is_instructor)
@get_workflow()
def export(request, wid):
    """Export the logs from the given workflow

    :param request: HTML request
    :param pk: pk of the workflow to export
    :return: Return a CSV download of the logs
    """
    dataset = LogResource().export(
        Log.objects.filter(user=request.user, workflow__id=wid)
    )

    # Create the response as a csv download
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs.csv"'

    return response
