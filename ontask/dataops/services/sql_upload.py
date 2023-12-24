"""Upload/Merge dataframe from an SQL connection."""
from typing import Dict, Optional

from django import http
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _
import pandas as pd

import ontask
from ontask import models
from ontask.core import session_ops
from ontask.dataops import pandas
from ontask.dataops.services import common


def _load_df_from_sqlconnection(
        conn_item: models.SQLConnection,
        run_params: Dict,
) -> pd.DataFrame:
    """Load a DF from a SQL connection.

    :param conn_item: SQLConnection object with the connection parameters.
    :param run_params: Dictionary with the execution parameters.
    :return: Data frame or raise an exception.
    """
    if conn_item.db_password:
        password = conn_item.db_password
    else:
        password = run_params['db_password']

    if conn_item.db_table:
        table_name = conn_item.db_table
    else:
        table_name = run_params['db_table']

    db_engine = pandas.create_db_engine(
        dialect=conn_item.conn_type,
        driver=conn_item.conn_driver,
        username=conn_item.db_user,
        password=password,
        host=conn_item.db_host,
        dbname=conn_item.db_name)

    # Try to fetch the data
    data_frame = pd.read_sql_table(table_name, db_engine)

    # Remove the engine
    db_engine.dispose()

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return pandas.detect_datetime_columns(data_frame)


def sql_upload_step_one(
        request: http.HttpRequest,
        workflow: models.Workflow,
        conn: models.SQLConnection,
        run_params: Dict,
):
    """Perform the first step to load a data frame from a SQL connection.

    :param request: Request received.
    :param workflow: Workflow being processed.
    :param conn: Database connection object.
    :param run_params: Dictionary with the additional run parameters.
    :return: Nothing, it creates the new dataframe in the database
    """
    # Process SQL connection using pandas
    data_frame = _load_df_from_sqlconnection(conn, run_params)
    # Verify the data frame
    pandas.verify_data_frame(data_frame)

    # Store the data frame in the DB.
    # Get frame info with three lists: names, types and is_key
    frame_info = pandas.store_temporary_dataframe(data_frame, workflow)

    # Dictionary to populate gradually throughout the sequence of steps. It
    # is stored in the session.
    session_ops.set_payload(
        request,
        {
            'initial_column_names': frame_info[0],
            'column_types': frame_info[1],
            'src_is_key_column': frame_info[2],
            'step_1': reverse(
                'dataops:sqlupload_start',
                kwargs={'pk': conn.id}),
            'log_upload': models.Log.WORKFLOW_DATA_SQL_UPLOAD})


class ExecuteSQLUpload:
    """Process the SQL upload operation in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.WORKFLOW_DATA_SQL_UPLOAD

    def execute_operation(
            self,
            user,
            workflow: Optional[models.Workflow] = None,
            action: Optional[models.Action] = None,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
    ):
        """Perform a SQL upload asynchronously.

        :param user: User object
        :param workflow: Optional workflow object
        :param action: Empty
        :param payload: has fields:
          - connection_id: PK of the connection object to use
          - dst_key: Key column in the existing dataframe (if any) for merge
          - src_key: Key column in the external dataframe (for merge)
          - how_merge: Merge method: inner, outer, left, right
          - db_password: Encoded password if not stored in the connection
          - db_table: Table name if not stored in the connection
        :param log_item: Optional logitem object.
        :return: Elements to add to the "extend" field. Empty list in this case
                 Upload/merge the data in the given workflow.
        """
        del action

        # Get the connection
        conn = models.SQLConnection.objects.filter(
            pk=payload['connection_id']).first()
        if not conn:
            msg = _('Incorrect connection identifier.')
            log_item.payload['error'] = msg
            log_item.save(update_fields=['payload'])
            raise ontask.OnTaskException(msg)

        # Get the dataframe from the connection
        src_df = _load_df_from_sqlconnection(conn, payload)

        # Create session
        session = common.create_session()

        common.access_workflow(user, session, workflow.id, log_item)

        # IDEA: How to deal with failure to acquire access?
        #       Include a setting with the time to wait and number of retries?

        pandas.perform_dataframe_set_or_update(
            workflow,
            src_df,
            common.get_how_merge(payload, log_item),
            common.get_key(payload, 'src_key', log_item),
            common.get_key(payload, 'dst_key', log_item),
            log_item)
