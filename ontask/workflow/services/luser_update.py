"""Functions to support task execcution for workflows."""
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import gettext

from ontask import models
from ontask.dataops import sql

RANDOM_PWD_LENGTH = 50


class ExecuteUpdateWorkflowLUser:
    """Update the LUSER field in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.WORKFLOW_UPDATE_LUSERS

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Recalculate lusers field.

        Recalculate the elements in field lusers of the workflow based on the
        fields luser_email_column and luser_email_column_MD5

        :param user: User object that is executing the action
        :param workflow: Workflow being processed (if applicable)
        :param action: Action being executed (if applicable)
        :param payload: Dictionary with the execution parameters
        :param log_item: Identifier of the object where the status is reflected
        :return: Nothing, the result is stored in the log with log_id
        """
        del action
        if not log_item and self.log_event:
            log_item = workflow.log(
                user,
                operation_type=self.log_event,
                **payload)

        # First get the log item to make sure we can record diagnostics
        try:
            # Get the column content
            emails = sql.get_rows(
                workflow.get_data_frame_table_name(),
                column_names=[workflow.luser_email_column.name])

            luser_list = []
            created = 0
            for row in emails:
                uemail = row[workflow.luser_email_column.name]
                luser = get_user_model().objects.filter(email=uemail).first()
                if not luser:
                    # Create user
                    if settings.DEBUG:
                        # Define users with the same password in development
                        password = 'boguspwd'  # NOQA
                    else:
                        password = get_random_string(length=RANDOM_PWD_LENGTH)
                    luser = get_user_model().objects.create_user(
                        email=uemail,
                        password=password,
                    )
                    created += 1

                luser_list.append(luser)

            # Assign result
            workflow.lusers.set(luser_list)
            workflow.lusers_is_outdated = False
            workflow.save()

            # Report status
            log_item.payload['total_users'] = emails.rowcount
            log_item.payload['new_users'] = created
            log_item.payload['status'] = gettext(
                'Learner emails successfully updated.',
            )
            log_item.save(update_fields=['payload'])

            # Reflect status in the log event
            log_item.payload['status'] = 'Execution finished successfully'
            log_item.save(update_fields=['payload'])
        except Exception as exc:
            log_item.payload['status'] = gettext('Error: {0}').format(exc)
            log_item.save(update_fields=['payload'])
