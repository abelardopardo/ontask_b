# -*- coding: utf-8 -*-

"""Services to process dataframes."""
from ontask.dataops.services.athena import (
    create_athena_connection_admintable,
    create_athena_connection_runtable)
from ontask.dataops.services.connections import (
    ConnectionTableAdmin, ConnectionTableSelect, clone_connection, delete, toggle)
from ontask.dataops.services.connections_sql import (
    create_sql_connection_admintable,
    sql_connection_select_table)
from ontask.dataops.services.dataframeupload import (
    batch_load_df_from_athenaconnection, load_df_from_csvfile,
    load_df_from_excelfile, load_df_from_googlesheet, load_df_from_s3,
    process_object_column)
from ontask.dataops.services.errors import OnTasDataopsPluginInstantiationError
from ontask.dataops.services.increase_track import ExecuteIncreaseTrackCount
from ontask.dataops.services.plugin_admin import (
    PluginAdminTable, load_plugin, refresh_plugin_data)
from ontask.dataops.services.plugin_execute import ExecuteRunPlugin
from ontask.dataops.services.plugin_run import (
    create_model_table, plugin_queue_execution)
from ontask.dataops.services.row import create_row, update_row_values
from ontask.dataops.services.sql_upload import (
    ExecuteSQLUpload, sql_upload_step_one)
from ontask.dataops.services.upload_steps import (
    upload_prepare_step_four, upload_step_four, upload_step_two)
