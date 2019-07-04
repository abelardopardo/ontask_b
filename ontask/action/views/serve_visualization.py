# -*- coding: utf-8 -*-

"""View to serve a visualization through a URL."""

from django.core import signing
from django.http import HttpRequest, HttpResponse, Http404
from django.views.decorators.http import require_http_methods

from ontask.dataops.sql import get_row
from ontask.workflow.models import Workflow, Column


def _generate_plotly_image(row):
    """Generate a PNG array of bytes with the data in the row.

    :param row: Dictionary with the data in the row

    :return: object with the binary bytes encoding the image
    """
    # import plotly.plotly as py
    # import plotly.graph_objs as go
    # import plotly.io as pio
    # # data = [go.Histogram()]
    # fig = go.Figure()
    # fig.add_histogram(
    #     x=["FEIT", "FEIT", "FSCI", "SMED", "FSCI", "FSCI", "FEIT", "FASS",
    #        "FSCI", "FSCI", "FASS", "SMED", "SMED", "FSCI"],
    #     autobinx=True,
    #     histnorm="",
    #     name="Program",
    #     type="histogram")
    # pio.write_image(fig, 'xxx.png')
    #
    return None


@require_http_methods(['GET'])
def serve_visualization(
    request: HttpRequest
) -> HttpResponse:
    """Serve a request for a visualization.

    Function that given a request, extracts from a given encrypted string (v)
    a json object with user id and column id, creates the visualization
    (if needed) and returns it as an image.

    The user id and column id are provided as part of the unique parameter

    :param request: HTTP request

    :return:
    """
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
    if not all(dkey in viz_info for dkey in ['kname', 'kvalue', 'colid']):
        raise Http404

    key_name = viz_info['key_name']
    key_value = viz_info['key_value']

    try:
        int(viz_info['colid'])
    except:
        raise Http404

    column = Column.objects.filter(pk=int(viz_info['colid'])).first()
    if not column:
        raise Http404

    # Get the row from the table
    row = get_row(
        column.workflow.get_data_frame_table_name(),
        key_name,
        key_value,
        column_names=[column.name],
    )

    image_bytes = _generate_plotly_image(row)

    return HttpResponse(image_bytes, content_type="image/png")
