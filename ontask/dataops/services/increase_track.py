"""Function to increase the tracking column in a workflow."""
from typing import Dict, Optional

from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.translation import gettext

from ontask import models, CELERY_LOGGER
from ontask.dataops import sql


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
        """Process track requests asynchronously.

        :param user: User object
        :param workflow: Optional workflow object
        :param action: Optional action object
        :param payload: has fields method and get_dict with the request
        method and the get dictionary.
        :param log_item: Optional log item object.
        :return: Nothing
        """
        del user, workflow, action, log_item

        CELERY_LOGGER.debug('Executing increase track count')

        method = payload.get('method')
        if method != 'GET':
            # Only GET requests are accepted
            msg = gettext('Non-GET request received in Track URL')
            CELERY_LOGGER.error(msg)
            raise Exception(msg)

        get_dict = payload.get('get_dict')
        if get_dict is None:
            msg = gettext('No dictionary in Track URL')
            CELERY_LOGGER.error(msg)
            raise Exception(msg)

        # Obtain the track_id from the request
        track_id = get_dict.get('v')
        if not track_id:
            msg = gettext('No track_id found in request')
            CELERY_LOGGER.error(msg)
            raise Exception(msg)

        # If the track_id is not correctly signed, finish.
        try:
            track_id = signing.loads(track_id)
        except signing.BadSignature:
            msg = gettext('Bad signature in track_id')
            CELERY_LOGGER.error(msg)
            raise Exception(msg)

        # The request is legit and the value has been verified. Track_id has
        # now the dictionary with the tracking information

        # Get the objects related to the ping
        user = get_user_model().objects.filter(
            email=track_id['sender']).first()
        if not user:
            msg = gettext('Incorrect user email %s')
            CELERY_LOGGER.error(msg, track_id['sender'])
            raise Exception(msg, track_id['sender'])

        action = models.Action.objects.filter(pk=track_id['action']).first()
        if not action:
            raise Exception(
                gettext('Incorrect action id %s'),
                track_id['action'])

        # Extract the relevant fields from the track_id
        column_dst = track_id.get('column_dst', '')
        column_to = track_id.get('column_to', '')
        msg_to = track_id.get('to', '')

        column = action.workflow.columns.filter(name=column_dst).first()
        if not column:
            # If the column does not exist, we are done
            raise Exception(gettext('Column %s does not exist'), column_dst)

        log_payload = {
            'to': msg_to,
            'email_column': column_to,
            'column_dst': column_dst}

        # If the track comes with column_dst, the event needs to be reflected
        # back in the data frame
        if column_dst:
            try:
                # Increase the relevant cell by one
                sql.increase_row_integer(
                    action.workflow.get_data_frame_table_name(),
                    column_dst,
                    column_to,
                    msg_to)
            except Exception as exc:
                log_payload['EXCEPTION_MSG'] = str(exc)
            else:
                # Get the tracking column and update all the conditions in the
                # actions that have this column as part of their formulas
                # FIX: Too aggressive?
                track_col = action.workflow.columns.get(name=column_dst)
                for act in action.workflow.actions.all():
                    act.update_selected_row_counts(track_col)

        # Record the event
        action.log(user, self.log_event, **log_payload)
