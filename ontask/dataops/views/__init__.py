# -*- coding: utf-8 -*-

"""Package with the dataops views."""

from ontask.dataops.views.csvupload import csvupload_start
from ontask.dataops.views.excelupload import excelupload_start
from ontask.dataops.views.googlesheetupload import googlesheetupload_start
from ontask.dataops.views.plugin_admin import (
    diagnose, moreinfo, plugin_admin, plugin_toggle,
)
from ontask.dataops.views.row import row_create, row_update
from ontask.dataops.views.s3upload import s3upload_start
from ontask.dataops.views.connection_admin import (
    sql_connection_admin_index, athena_connection_admin_index,
    sql_connection_view, athena_connection_view,
    sql_connection_edit, athena_connection_edit,
    sql_connection_clone, athena_connection_clone,
    sql_connection_delete, athena_connection_delete,
    sqlconn_toggle, athenaconn_toggle)
from ontask.dataops.views.connection_instructor import (
    sql_connection_instructor_index, athena_connection_instructor_index)
from ontask.dataops.views.sqlupload import sqlupload_start
from ontask.dataops.views.athenaupload import athenaupload_start
from ontask.dataops.views.transform import plugin_invoke, transform_model
from ontask.dataops.views.upload import (
    upload_s2, upload_s3, upload_s4, uploadmerge,
)
