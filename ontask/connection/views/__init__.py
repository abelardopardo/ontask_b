# -*- coding: utf-8 -*-

"""Package with the connection views."""
from ontask.connection.views.admin import (
    athena_connection_admin_index, athena_connection_clone,
    athena_connection_delete, athena_connection_edit, athena_connection_view,
    athenaconn_toggle, sql_connection_admin_index, sql_connection_clone,
    sql_connection_delete, sql_connection_edit, sql_connection_view,
    sqlconn_toggle,
)
from ontask.connection.views.instructor import (
    athena_connection_instructor_index, sql_connection_index,
)
