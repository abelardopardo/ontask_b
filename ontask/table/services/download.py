# -*- coding: utf-8 -*-

"""Functions to support download a table in CSV format."""
from django import http
import pandas as pd


def create_response_with_csv(data_frame: pd.DataFrame) -> http.HttpResponse:
    """Create a HTTP Response to download a data frame in CSV format.

    :param data_frame: Data frame to send
    :return: HttpResponse
    """
    # Create the response object
    response = http.HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="ontask_table.csv"'

    # Dump the data frame as the content of the response object
    data_frame.to_csv(
        path_or_buf=response,
        sep=str(','),
        index=False,
        encoding='utf-8')

    return response
