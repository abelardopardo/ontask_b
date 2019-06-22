# -*- coding: utf-8 -*-

"""View to serve a visualization through a URL."""

from django.core import signing
from django.http import HttpRequest, HttpResponse, Http404
from django.views.decorators.http import require_http_methods

from dataops.sql import get_row
from workflow.models import Workflow

def _generate_plotly_image(row):
    """Generate a PNG array of bytes with the data in the row.

    :param row: Dictionary with the data in the row

    :return: object with the binary bytes encoding the image
    """

    return None


@require_http_methods(['GET'])
def serve_visualization(
    request: HttpRequest,
    wid: Workflow,
) -> HttpResponse:
    """Serve a request for a visualization.

    Function that given a request, and a workflow id, extracts from a given
    encrypted string (v) the key name, key value and column name and returns
    the corresponding visualization.

    The key name, key value and column name are provided as an encrypted string

    :param request: HTTP request

    :param workflow: Workflow

    :return:
    """
    # Obtain first the workflow ID, no need to lock the content as it is only a
    # read operation.
    workflow = Workflow.objects.filter(id=wid).first()
    if not workflow:
        raise Http404

    # Extract the encrypted information from the request variable
    viz_info = request.GET.get('v')
    if not viz_info:
        raise Http404

    # Decode the string
    try:
        viz_info = signing.loads(viz_info)
    except signing.BadSignature:
        raise Http404

    # Verify that all three keys are in the dictionary
    if not all(dkey in viz_info for dkey in [
        'key_name', 'key_value', 'column_name']
    ):
        raise Http404

    key_name = viz_info['key_name']
    key_value = viz_info['key_value']
    column_name = viz_info['column_name']

    # Key name and column name must be correct columns
    if not all(cname in workflow.columns.all()
               for cname in [key_name, column_name]
    ):
        raise Http404

    # Get the row from the table
    row = get_row(
        workflow.get_data_frame_table_name(),
        key_name,
        key_value,
        column_names=[column_name],
    )

    image_bytes = _generate_plotly_image(row)

    return HttpResponse(image_bytes, content_type="image/png")
