# -*- coding: utf-8 -*-

"""Functions to download a table in CSV format."""

from typing import Optional

import pandas as pd
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse

from ontask.apps.dataops.pandas import get_subframe
from ontask.decorators import get_view, get_workflow
from ontask.permissions import is_instructor
from ontask.apps.table.models import View
from ontask.apps.workflow.models import Workflow


def _respond_csv(data_frame: pd.DataFrame) -> HttpResponse:
    """Create a HTTP Response to download a data frame in CSV format.

    :param data_frame: Data frame to send

    :return: HttpResponse
    """
    # Create the response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ontask_table.csv"'

    # Dump the data frame as the content of the response object
    data_frame.to_csv(
        path_or_buf=response,
        sep=str(','),
        index=False,
        encoding='utf-8')

    return response


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns'])
def csvdownload(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Download the data in the workflow.

    :param request: HTML request

    :param workflow: Set by the decorator to the current workflow.

    :return: Return a CSV download of the data in the table
    """
    # Fetch the data frame
    return _respond_csv(
        get_subframe(
            workflow.get_data_frame_table_name(),
            None,
            workflow.get_column_names(),
        ),
    )


@user_passes_test(is_instructor)
@get_view(pf_related=['columns', 'views'])
def csvdownload_view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    view: Optional[View] = None,
) -> HttpResponse:
    """Download the data in a given view.

    :param request: HTML request

    :param pk: View ID

    :param workflow: Set by the decorator to the current workflow.

    :param view: Set by the decorator to the view with the given PK

    :return: Return a CSV download of the data in the table
    """
    # Fetch the data frame
    return _respond_csv(
        get_subframe(
            workflow.get_data_frame_table_name(),
            view.formula,
            [col.name for col in view.columns.all()],
        ),
    )
