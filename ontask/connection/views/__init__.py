"""Package with the connection views."""
from ontask.connection.views.athena import (
    AthenaConnectionAdminIndexView, AthenaConnectionCreateView,
    AthenaConnectionIndexView, AthenaConnectionEditView)
from ontask.connection.views.common import (
    ConnectionAdminIndexView, ConnectionIndexView, ConnectionShowView,
    ConnectionBaseCreateEditView, ConnectionDeleteView, ConnectionCloneView,
    ConnectionToggleView)
from ontask.connection.views.sql import (
    SQLConnectionAdminIndexView, SQLConnectionCreateView,
    SQLConnectionEditView, SQLConnectionIndexView)
