# -*- coding: utf-8 -*-

"""Function to increase the tracking column in a workflow."""
from typing import Dict, Optional

from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.translation import ugettext

from ontask import models
from ontask.dataops.sql.row_queries import increase_row_integer
from ontask.tasks.execute import task_execute_factory


class ExecuteIncreaseTrackCount:
    """Process the increase track count in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.ACTION_EMAIL_READ

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Function to process track requests asynchronously.

        :param user: User object
        :param workflow: Optional workflow object
        :param action: Optional action object
        :param payload: has fields method and get_dict with the request
        method and the get dictionary.
        :param log_item: Optional logitem object.
        :returns: nothing
        """
        method = payload.get('method')
        if method != 'GET':
            # Only GET requests are accepted
            raise Exception(ugettext('Non-GET request received in Track URL'))

        get_dict = payload.get('get_dict')
        if get_dict is None:
            raise Exception(ugettext('No dictionary in Track URL'))

        # Obtain the track_id from the request
        track_id = get_dict.get('v')
        if not track_id:
            raise Exception(ugettext('No track_id found in request'))

        # If the track_id is not correctly signed, finish.
        try:
            track_id = signing.loads(track_id)
        except signing.BadSignature:
            raise Exception(ugettext('Bad signature in track_id'))

        # The request is legit and the value has been verified. Track_id has
        # now the dictionary with the tracking information

        # Get the objects related to the ping
        user = get_user_model().objects.filter(
            email=track_id['sender']).first()
        if not user:
            raise Exception(
                ugettext('Incorrect user email %s'),
                track_id['sender'])

        action = models.Action.objects.filter(pk=track_id['action']).first()
        if not action:
            raise Exception(
                ugettext('Incorrect action id %s'),
                track_id['action'])

        # Extract the relevant fields from the track_id
        column_dst = track_id.get('column_dst', '')
        column_to = track_id.get('column_to', '')
        msg_to = track_id.get('to', '')

        column = action.workflow.columns.filter(name=column_dst).first()
        if not column:
            # If the column does not exist, we are done
            raise Exception(ugettext('Column %s does not exist'), column_dst)

        log_payload = {
            'to': msg_to,
            'email_column': column_to,
            'column_dst': column_dst}

        # If the track comes with column_dst, the event needs to be reflected
        # back in the data frame
        if column_dst:
            try:
                # Increase the relevant cell by one
                increase_row_integer(
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
        action.log(user, self.log_event, **log_payload)


task_execute_factory.register_producer(
    models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
    ExecuteIncreaseTrackCount())
