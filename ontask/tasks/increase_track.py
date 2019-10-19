# -*- coding: utf-8 -*-

"""Function to increase the tracking column in a workflow."""

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.translation import ugettext

import ontask.dataops.sql
from ontask.models import Action, Log
from ontask.tasks.basic import logger


@shared_task
def increase_track_count_task(method, get_dict):
    """
    Function to process track requests asynchronously.

    :param method: GET or POST received in the request
    :param get_dict: GET dictionary received in the request
    :return: If correct, increases one row of the DB by one
    """

    if method != 'GET':
        # Only GET requests are accepted
        logger.error(ugettext('Non-GET request received in Track URL'))
        return False

    # Obtain the track_id from the request
    track_id = get_dict.get('v')
    if not track_id:
        logger.error(ugettext('No track_id found in request'))
        # No track id, nothing to do
        return False

    # If the track_id is not correctly signed, finish.
    try:
        track_id = signing.loads(track_id)
    except signing.BadSignature:
        logger.error(ugettext('Bad signature in track_id'))
        return False

    # The request is legit and the value has been verified. Track_id has now
    # the dictionary with the tracking information

    # Get the objects related to the ping
    user = get_user_model().objects.filter(email=track_id['sender']).first()
    if not user:
        logger.error(ugettext('Incorrect user email %s'), track_id['sender'])
        return False

    action = Action.objects.filter(pk=track_id['action']).first()
    if not action:
        logger.error(
            ugettext('Incorrect action id %s'),
            track_id['action'])
        return False

    # Extract the relevant fields from the track_id
    column_dst = track_id.get('column_dst', '')
    column_to = track_id.get('column_to', '')
    msg_to = track_id.get('to', '')

    column = action.workflow.columns.filter(name=column_dst).first()
    if not column:
        # If the column does not exist, we are done
        logger.error(ugettext('Column %s does not exist'), column_dst)
        return False

    log_payload = {
        'to': msg_to,
        'email_column': column_to,
        'column_dst': column_dst}

    # If the track comes with column_dst, the event needs to be reflected
    # back in the data frame
    if column_dst:
        try:
            # Increase the relevant cell by one
            ontask.dataops.sql.row_queries.increase_row_integer(
                action.workflow.get_data_frame_table_name(),
                column_dst,
                column_to,
                msg_to
            )
        except Exception as e:
            log_payload['EXCEPTION_MSG'] = str(e)
        else:
            # Get the tracking column and update all the conditions in the
            # actions that have this column as part of their formulas
            # FIX: Too aggressive?
            track_col = action.workflow.columns.get(name=column_dst)
            for action in action.workflow.actions.all():
                action.update_n_rows_selected(track_col)

    # Record the event
    action.log(user, Log.ACTION_EMAIL_READ, **log_payload)

    return True
