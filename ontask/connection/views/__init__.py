# -*- coding: utf-8 -*-

"""Package with the connection views."""
from ontask.connection.views.athena import (
    AthenaConnectionAdminIndexView, athena_connection_clone,
    athena_connection_delete, athena_connection_edit,
    athena_connection_instructor_index,
    athena_connection_view, athenaconn_toggle)
from ontask.connection.views.sql import (
    SQLConnectionAdminIndexView, sql_connection_clone, sql_connection_delete,
    sql_connection_edit, sql_connection_index, sql_connection_toggle,
    sql_connection_view)
