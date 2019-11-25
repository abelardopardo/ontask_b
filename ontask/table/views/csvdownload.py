# -*- coding: utf-8 -*-

"""Views  to download a table in CSV format."""

from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse

from ontask import models
from ontask.core.decorators import get_view, get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.pandas import get_subframe
from ontask.table import services


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns'])
def csvdownload(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Download the data in the workflow.

    :param request: HTML request
    :param workflow: Set by the decorator to the current workflow.
    :return: Return a CSV download of the data in the table
    """
    return services.create_response_with_csv(
        get_subframe(
            workflow.get_data_frame_table_name(),
            None,
            workflow.get_column_names()))


@user_passes_test(is_instructor)
@get_view(pf_related=['columns', 'views'])
def csvdownload_view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    view: Optional[models.View] = None,
) -> HttpResponse:
    """Download the data in a given view.

    :param request: HTML request
    :param pk: View ID
    :param workflow: Set by the decorator to the current workflow.
    :param view: Set by the decorator to the view with the given PK
    :return: Return a CSV download of the data in the table
    """
    return services.create_response_with_csv(
        get_subframe(
            workflow.get_data_frame_table_name(),
            view.formula,
            [col.name for col in view.columns.all()]))
