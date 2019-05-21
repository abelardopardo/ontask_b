# -*- coding: utf-8 -*-

"""Views to run the personalized zip action."""
import zipfile
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from action.evaluate.action import evaluate_action
from action.forms import ZipActionForm
from action.models import Action
from action.payloads import (
    ZipPayload, action_session_dictionary, get_action_info,
)
from action.views.run_email import html_body
from dataops.sql.row_queries import get_rows
from logs.models import Log
from ontask.decorators import get_action, get_workflow
from ontask.permissions import is_instructor
from workflow.models import Workflow


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def zip_action(
    req: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Request data to create a zip file.

    Form asking for participant column, user file name column, file suffix,
    if it is a ZIP for Moodle and confirm users step.

    :param req: HTTP request (GET)
    :param pk: Action key
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    action_info = get_action_info(
        req.session,
        ZipPayload,
        initial_values={
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:zip_done'),
        }
    )

    # Create the form to ask for the email subject and other information
    form = ZipActionForm(
        req.POST or None,
        column_names=[col.name for col in workflow.columns.all()],
        action=action,
        action_info=action_info,
    )

    if req.method == 'POST' and form.is_valid():
        if action_info['confirm_items']:
            # Add information to the session object to execute the next pages
            action_info['button_label'] = ugettext('Create ZIP')
            action_info['valuerange'] = 2
            action_info['step'] = 2
            req.session[action_session_dictionary] = action_info.get_store()

            return redirect('action:item_filter')

        # Go straight to the final step.
        return run_zip_done(
            req,
            action_info=action_info,
            workflow=workflow)

    # Render the form
    return render(
        req,
        'action/action_zip_step1.html',
        {'action': action,
         'num_msgs': action.get_rows_selected(),
         'form': form})


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def run_zip_done(
    request: HttpRequest,
    action_info: Optional[ZipPayload] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create the zip object, send it for download and render the DONE page.

    :param request: HTTP request (GET)
    :param action_info: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """
    # Get the payload from the session if not given
    action_info = get_action_info(
        request.session,
        ZipPayload,
        action_info=action_info)
    if action_info is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect ZIP action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = workflow.actions.filter(pk=action_info['action_id']).first()
    if not action:
        return redirect('home')

    # Log the event
    log_item = Log.objects.register(
        request.user,
        Log.DOWNLOAD_ZIP_ACTION,
        action.workflow,
        {
            'action': action.name,
            'action_id': action.id,
            'user_fname_column': action_info['user_fname_column'],
            'participant_column': action_info['item_column'],
            'file_suffix': action_info['file_suffix'],
            'zip_for_moodle': action_info['zip_for_moodle'],
            'exclude_values': action_info['exclude_values'],
        })

    # Successful processing.
    return render(request, 'action/action_zip_done.html', {})


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_zip_export(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create a zip with the personalised text and return it as response.

    :param request: Request object with a Dictionary with all the required
    information
    :return: Response (download)
    """
    # Get the payload from the session if not given
    action_info = get_action_info(request.session)
    if not action_info:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect ZIP action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = workflow.actions.filter(pk=action_info['action_id']).first()
    if not action:
        return redirect('home')

    # Create the file name template
    if action_info['zip_for_moodle']:
        file_name_template = (
            '{user_fname}_{part_id}_assignsubmission_file_'
        )
    else:
        if action_info['user_fname_column']:
            file_name_template = '{part_id}_{user_fname}_'
        else:
            file_name_template = '{part_id}'
    file_name_template += action_info.get('file_suffix', 'feedback.html')

    # Create the ZIP with the eval data tuples and return it for download
    sbuf = create_zip(
        create_eval_data_tuple(
            action,
            action_info['item_column'],
            action_info['exclude_values'],
            action_info['user_fname_column'],
        ),
        action_info['zip_for_moodle'],
        file_name_template)

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = None
    request.session.save()

    return create_response(sbuf)


def create_eval_data_tuple(
    action: Action,
    participant_column: str,
    exclude_values: List,
    user_fname_column: Optional[str],
) -> List[Tuple[str, str, str]]:
    """Evaluate text and create list of tuples [filename, part id, text].

    Evaluate the conditions in the actions based on the given
    participant_column excluding the values in exclude_values. This returns a
    list with tuples [action text, None, participant column value]. Process
    that list to insert as second element of the tuple the corresponding
    value in user_fname_column (if given).

    The final result is a list of triplets with:

    - Filename
    - part id as extracted from the participation column
    - HTML body text

    :param action: Action being processed
    :param participant_column: The
    :param exclude_values: List of values to exclude from evaluation
    :param user_fname_column: Column name to use for filename creation
    :return: List[text, text, text]
    """
    # Obtain the personalised text
    action_evals = evaluate_action(
        action,
        column_name=participant_column,
        exclude_values=exclude_values)

    if user_fname_column:
        # Get the user_fname_column values
        user_fname_data = get_rows(
            action.workflow.get_data_frame_table_name(),
            column_names=[user_fname_column],
            filter_formula=None).fetchall()
    else:
        # Array of Nones for the merge
        user_fname_data = [''] * len(action_evals)

    return [
        (user_fname, part_id, html_body.format(msg_body))
        for msg_body, part_id, user_fname in zip(action_evals, user_fname_data)
    ]


def create_zip(
    files: List[Tuple[str, str, str]],
    for_moodle: bool,
    file_name_template: str,
) -> BytesIO:
    """Process the list of tuples in files and create the ZIP BytesIO object.

    :param files: List of triplets (user_fname, part_id,
    :param for_moodle:
    :param file_name_template:
    :return:
    """
    # Create the ZIP and return it for download
    sbuf = BytesIO()
    zf = zipfile.ZipFile(sbuf, 'w')
    for user_fname, part_id, msg_body in files:
        if for_moodle:
            # If a zip for Moodle, field is Participant [number]. Take the
            # number only
            part_id = part_id.split()[1]

        zf.writestr(
            file_name_template.format(user_fname=user_fname, part_id=part_id),
            str(msg_body),
        )
    zf.close()

    return sbuf


def create_response(sbuf: BytesIO) -> HttpResponse:
    """Given a zip buffer, create the HTTP Response to download it.

    :param sbuf: BytesIO storing the zipped content.
    :return: HttpResponse
    """
    suffix = datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = sbuf.getvalue()
    response = HttpResponse(compressed_content)
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = (
        'attachment; filename="ontask_zip_action_{0}.zip"'.format(suffix))
    response['Content-Length'] = str(len(compressed_content))

    return response
