"""Service functions to handle the upload steps."""
from typing import Dict, List, Tuple

from django import http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from ontask import models
from ontask.core import session_ops
from ontask.dataops import pandas, sql


def upload_step_two(
    request: http.HttpRequest,
    workflow: models.Workflow,
    select_column_data: Dict,
    upload_data: Dict,
) -> http.HttpResponse:
    """Process the received dataframe and either store or continue the merge.

    :param request: Http request received.
    :param workflow: workflow being processed.
    :param select_column_data: Dictionary with the upload/merge information
    (new column names, keep the keys)
    :param upload_data: Dictionary with the upload information.
    :return: Http Response
    """
    # We need to modify upload_data with the information received in the
    # post
    initial_columns = upload_data.get('initial_column_names')
    src_is_key_column = upload_data.get('src_is_key_column')
    keep_key_column = upload_data.get('keep_key_column')
    for idx in range(len(initial_columns)):
        new_name = select_column_data['new_name_%s' % idx]
        upload_data['rename_column_names'][idx] = new_name
        upload = select_column_data['upload_%s' % idx]
        upload_data['columns_to_upload'][idx] = upload

        if src_is_key_column[idx]:
            # If the column is key, check if the user wants to keep it
            keep_key_column[idx] = select_column_data['make_key_%s' % idx]

    if workflow.has_data_frame:
        # A Merge operation is required so move to Step 3
        return redirect('dataops:upload_s3')

    # This is the first data to be stored in the workflow. Save the uploaded
    # dataframe in the DB and finish.
    pandas.store_workflow_table(workflow, upload_data)

    # Update the session information
    session_ops.store_workflow_in_session(request, workflow)

    col_info = workflow.get_column_info()
    workflow.log(
        request.user,
        upload_data['log_upload'],
        column_names=col_info[0],
        column_types=col_info[1],
        column_unique=col_info[2])

    return redirect(reverse('table:display'))


def upload_prepare_step_four(upload_data: Dict) -> List[Tuple[str, bool, str]]:
    """Prepare a list with the summary of merge operation.

    :param upload_data: Dictionary with all the merge information.
    :return: List of triplets Name, boolean, Name to render the summary
    """
    # We are processing a GET request
    dst_column_names = upload_data['dst_column_names']
    dst_selected_key = upload_data['dst_selected_key']
    src_selected_key = upload_data['src_selected_key']
    # List of final column names
    final_columns = sorted(set().union(
        dst_column_names,
        upload_data['rename_column_names'],
    ))
    # Dictionary with (new src column name: (old name, is_uploaded?)
    src_info = {rname: (iname, upload) for (rname, iname, upload) in zip(
        upload_data['rename_column_names'],
        upload_data['initial_column_names'],
        upload_data['columns_to_upload'],
    )}

    # Create the strings to show in the table for each of the rows explaining
    # what is going to be the effect of the update operation over them.
    #
    # There are 8 cases depending on the column name being a key column,
    # in DST, SRC, if SRC is being renamed, and SRC is being loaded.
    #
    # Case 1: The column is the key column used for the merge (skip it)
    #
    # Case 2: in DST, NOT in SRC:
    #         Dst | |
    #
    # Case 3: in DST, in SRC, NOT LOADED
    #         Dst Name | <-- | Src new name (Ignored)
    #
    # Case 4: NOT in DST, in SRC, NOT LOADED
    #         | | Src new name (Ignored)
    #
    # Case 5: in DST, in SRC, Loaded, no rename:
    #         Dst Name (Update) | <-- | Src name
    #
    # Case 6: in DST, in SRC, loaded, rename:
    #         Dst Name (Update) | <-- | Src new name (Renamed)
    #
    # Case 7: NOT in DST, in SRC, loaded, no rename
    #         Dst Name (NEW) | <-- | src name
    #
    # Case 8: NOT in DST, in SRC, loaded, renamed
    #         Dst Name (NEW) | <-- | src name (renamed)
    #
    column_info = []
    for colname in final_columns:

        # Case 1: Skip the keys
        if colname == src_selected_key or colname == dst_selected_key:
            continue

        # Case 2: Column is in DST and left untouched (no counterpart in SRC)
        if colname not in list(src_info.keys()):
            column_info.append((colname, False, ''))
            continue

        # Get old name and if it is going to be loaded
        old_name, to_load = src_info[colname]

        # Column is not going to be loaded anyway
        if not to_load:
            if colname in dst_column_names:
                # Case 3
                column_info.append((colname, False, colname + _(' (Ignored)')))
            else:
                # Case 4
                column_info.append(('', False, colname + _(' (Ignored)')))
            continue

        # Initial name on the dst data frame
        dst_name = colname
        # Column not present in DST, so it is a new column
        if colname not in dst_column_names:
            dst_name += _(' (New)')
        else:
            dst_name += _(' (Update)')

        src_name = colname
        if colname != old_name:
            src_name += _(' (Renamed)')

        # Cases 5 - 8
        column_info.append((dst_name, True, src_name))

    return column_info


def upload_step_four(
    request: http.HttpRequest,
    workflow: models.Workflow,
    upload_data: Dict,
) -> http.HttpResponse:
    """Perform the merge operation.

    :param request: Received request
    :param workflow: Workflow being processed
    :param upload_data: Dictionary with all the information about the merge.
    :return: HttpResponse
    """
    # Get the dataframes to merge
    try:
        dst_df = pandas.load_table(workflow.get_data_frame_table_name())
        src_df = pandas.load_table(workflow.get_upload_table_name())
    except Exception:
        return render(
            request,
            'error.html',
            {'message': _('Exception while loading data frame')})

    try:
        pandas.perform_dataframe_upload_merge(
            workflow,
            dst_df,
            src_df,
            upload_data)
    except Exception as exc:
        # Nuke the temporary table
        sql.delete_table(workflow.get_upload_table_name())
        col_info = workflow.get_column_info()
        workflow.log(
            request.user,
            models.Log.WORKFLOW_DATA_FAILEDMERGE,
            column_names=col_info[0],
            column_types=col_info[1],
            column_unique=col_info[2],
            error_message=str(exc))
        messages.error(request, _('Merge operation failed. ') + str(exc))
        return redirect(reverse('table:display'))

    col_info = workflow.get_column_info()
    workflow.log(
        request.user,
        upload_data['log_upload'],
        column_names=col_info[0],
        column_types=col_info[1],
        column_unique=col_info[2])
    session_ops.store_workflow_in_session(request, workflow)

    # Remove the upload_data payload from the session
    session_ops.flush_payload(request)

    return redirect(reverse('table:display'))
