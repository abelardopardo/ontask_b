# -*- coding: utf-8 -*-

"""Core elements of the application.

The constant ONTASK_FIELD_PREFIX is used in forms to avoid using column names
(they are given by the user and may pose a problem)
"""
from ontask.core.decorators import (
    ajax_required, get_action, get_column, get_columncondition, get_condition,
    get_view, get_workflow,
)
from ontask.core.forms import (
    DATE_TIME_WIDGET_OPTIONS, RestrictedFileField, column_to_field)
from ontask.core.manage_session import SessionPayload
from ontask.core.permissions import (
    UserIsInstructor, has_access, is_admin, is_instructor,
)
from ontask.core.session_ops import (
    store_workflow_in_session, store_workflow_nrows_in_session,
)
from ontask.core.tables import DataTablesServerSidePaging, OperationsColumn

ONTASK_UPLOAD_FIELD_PREFIX = '___ontask___upload_'

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
ONTASK_SELECT_FIELD_PREFIX = '___ontask___select_'

# Length of suffix to add to file names
ONTASK_SUFFIX_LENGTH = 512

