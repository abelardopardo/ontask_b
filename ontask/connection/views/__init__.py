"""Package with the connection views."""
from ontask.connection.views.common import (
    ConnectionAdminIndexView, ConnectionIndexView, ConnectionShowView,
    ConnectionBaseCreateEditView, ConnectionDeleteView, ConnectionCloneView,
    ConnectionToggleView)
from ontask.connection.views.athena import (
    AthenaConnectionAdminIndexView, AthenaConnectionCloneView,
    AthenaConnectionDeleteView, AthenaConnectionCreateView,
    AthenaConnectionIndexView, AthenaConnectionEditView,
    AthenaConnectionShowView, AthenaConnectionToggleView)
from ontask.connection.views.sql import (
    SQLConnectionAdminIndexView, SQLConnectionCloneView,
    SQLConnectionCreateView, SQLConnectionDeleteView, SQLConnectionEditView,
    SQLConnectionIndexView, SQLConnectionShowView, SQLConnectionToggleView)
