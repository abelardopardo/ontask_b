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
from ontask.dataops.views.sqlconnection import (
    sqlconn_add, sqlconn_clone, sqlconn_delete, sqlconn_edit, sqlconn_view,
    sqlconnection_admin_index, sqlconnection_instructor_index,
)
from ontask.dataops.views.athenaconnection import (
    athenaconn_add, athenaconn_clone, athenaconn_delete, athenaconn_edit,
    athenaconn_view, athenaconnection_admin_index,
    athenaconnection_instructor_index)
from ontask.dataops.views.sqlupload import sqlupload_start
from ontask.dataops.views.athenaupload import athenaupload_start
from ontask.dataops.views.transform import plugin_invoke, transform_model
from ontask.dataops.views.upload import (
    upload_s2, upload_s3, upload_s4, uploadmerge,
)
