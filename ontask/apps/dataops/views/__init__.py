# -*- coding: utf-8 -*-

"""Package with the dataops views."""

from ontask.apps.dataops.views.csvupload import csvupload_start
from ontask.apps.dataops.views.excelupload import excelupload_start
from ontask.apps.dataops.views.googlesheetupload import googlesheetupload_start
from ontask.apps.dataops.views.row import row_create, row_update
from ontask.apps.dataops.views.s3upload import s3upload_start
from ontask.apps.dataops.views.sqlconnection import (
    sqlconn_add, sqlconn_clone, sqlconn_delete, sqlconn_edit, sqlconn_view,
    sqlconnection_admin_index, sqlconnection_instructor_index,
)
from ontask.apps.dataops.views.sqlupload import sqlupload_start
from ontask.apps.dataops.views.transform import (
    plugin_invoke, transform_model
)
from ontask.apps.dataops.views.plugin_admin import (
    plugin_admin, diagnose, moreinfo,
    plugin_toggle,
)
from ontask.apps.dataops.views.upload import upload_s2, upload_s3, upload_s4, uploadmerge
