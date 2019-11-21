# -*- coding: utf-8 -*-

"""Methods to process the personalized zip action run request."""

import zipfile
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

from django import http
from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import redirect, render

from ontask import models
from ontask.action import forms
from ontask.action.evaluate.action import evaluate_action
from ontask.action.services.manager import ActionRunManager
from ontask.action.services.manager_factory import action_process_factory
from ontask.core import SessionPayload
from ontask.dataops.sql.row_queries import get_rows

html_body = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>title</title>
  </head>
  <body>
    {0}
  </body>
</html>"""


def _create_filename_template(
    payload: SessionPayload,
    user_fname_column: Optional[models.Column],
) -> str:
    """Create the filename template based on given parameters."""
    if payload['zip_for_moodle']:
        file_name_template = (
            '{user_fname}_{part_id}_assignsubmission_file_'
        )
    else:
        if user_fname_column:
            file_name_template = '{part_id}_{user_fname}_'
        else:
            file_name_template = '{part_id}'
    if payload['file_suffix']:
        file_name_template += payload['file_suffix']
    else:
        file_name_template += 'feedback.html'

    return file_name_template


def _create_eval_data_tuple(
    action: models.Action,
    item_column: models.Column,
    exclude_values: List,
    user_fname_column: Optional[models.Column],
) -> List[Tuple[str, str, str]]:
    """Evaluate text and create list of tuples [filename, part id, text].

    Evaluate the conditions in the actions based on the given
    item_column excluding the values in exclude_values. This returns a
    list with tuples [action text, None, participant column value]. Process
    that list to insert as second element of the tuple the corresponding
    value in user_fname_column (if given).

    The final result is a list of triplets with:

    - Filename
    - part id as extracted from the participation column
    - HTML body text

    :param action: Action being processed

    :param item_column: The column used to iterate

    :param exclude_values: List of values to exclude from evaluation

    :param user_fname_column: Column to use for filename creation

    :return: List[Tuple[text, text, text]]
    """
    # Obtain the personalised text
    action_evals = evaluate_action(
        action,
        column_name=item_column.name,
        exclude_values=exclude_values)

    if user_fname_column:
        # Get the user_fname_column values
        user_fname_data = [row[user_fname_column.name] for row in get_rows(
            action.workflow.get_data_frame_table_name(),
            column_names=[user_fname_column.name],
            filter_formula=None).fetchall()]
    else:
        # Array of empty strings to concatenate
        user_fname_data = [''] * len(action_evals)

    return [
        (user_fname, part_id, html_body.format(msg_body))
        for (msg_body, part_id), user_fname in
        zip(action_evals, user_fname_data)
    ]


def create_and_send_zip(
    session: SessionBase,
    action: models.Action,
    item_column: models.Column,
    user_fname_column: Optional[models.Column],
    payload: SessionPayload,
) -> http.HttpResponse:
    """Process the list of tuples in files and create the ZIP BytesIO object.

    :param files: List of triplets (user_fname, part_id,
    :param for_moodle:
    :param file_name_template:
    :return:
    """
    files = _create_eval_data_tuple(
        action,
        item_column,
        payload.get('exclude_values', []),
        user_fname_column)
    file_name_template = _create_filename_template(payload, user_fname_column)

    # Create the ZIP and return it for download
    sbuf = BytesIO()
    zf = zipfile.ZipFile(sbuf, 'w')
    for user_fname, part_id, msg_body in files:
        if payload['zip_for_moodle']:
            # If a zip for Moodle, field is Participant [number]. Take the
            # number only
            part_id = part_id.split()[1]

        zf.writestr(
            file_name_template.format(user_fname=user_fname, part_id=part_id),
            str(msg_body),
        )
    zf.close()

    SessionPayload.flush(session)

    suffix = datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = sbuf.getvalue()
    response = http.HttpResponse(compressed_content)
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = (
        'attachment; filename="ontask_zip_action_{0}.zip"'.format(suffix))
    response['Content-Length'] = str(len(compressed_content))

    return response


class ActionManagerZip(ActionRunManager):
    """Class to serve running an email action."""

    def process_run_request_done(
        self,
        request: http.HttpRequest,
        workflow: models.Action,
        payload: SessionPayload,
        action: Optional[models.Action] = None,
    ) -> http.HttpResponse:
        """Finish processing the valid POST request.

        Get the action and redirect to the action_done page to prompt the
        download of the zip file.
        """
        # Get the information from the payload
        if not action:
            action = workflow.actions.filter(pk=payload['action_id']).first()
            if not action:
                return redirect('home')

        self._create_log_event(
            request.user,
            action,
            payload.get_store())

        # Successful processing.
        return render(request, 'action/action_zip_done.html', {})


action_process_factory.register_producer(
    models.action.ZIP_OPERATION,
    ActionManagerZip(
        run_form_class=forms.ZipActionRunForm,
        run_template='action/action_zip_step1.html',
        log_event=models.Log.ACTION_RUN_ZIP))
