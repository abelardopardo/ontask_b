# -*- coding: utf-8 -*-

"""Core elements of the application.

The constant ONTASK_FIELD_PREFIX is used in forms to avoid using column names
(they are given by the user and may pose a problem)
"""
from ontask.core.checks import (
    check_key_columns, check_workflow, fix_non_unique_object_names)
from ontask.core.decorators import (
    ajax_required, get_action, get_column, get_columncondition, get_condition,
    get_view, get_workflow, get_filter)

from ontask.core.forms import (
    DATE_TIME_WIDGET_OPTIONS, RestrictedFileField, column_to_field)

from ontask.core.manage_session import SessionPayload
from ontask.core.permissions import (
    GROUP_NAMES, UserIsInstructor, has_access, is_admin, is_instructor,
    SingleWorkflowMixin, JSONResponseMixin, JSONFormResponseMixin,
    RequestWorkflowView, SingleActionMixin, error_redirect,
    store_workflow_in_session)

from ontask.core.session_ops import (
    _store_workflow_nrows_in_session, remove_workflow_from_session)

from ontask.core.tables import DataTablesServerSidePaging, OperationsColumn

from ontask.core.serializers import OnTaskObjectIdField, OnTaskVersionField

ONTASK_UPLOAD_FIELD_PREFIX = '___ontask___upload_'

# Field prefix to use in forms to avoid using column names (they are given by
# the user and may pose a problem (injection bugs)
ONTASK_SELECT_FIELD_PREFIX = '___ontask___select_'

# Field to use to name the scheduled tasks (use the ScheduledOperation id
ONTASK_SCHEDULED_TASK_NAME_TEMPLATE = '___ontask___scheduled_{0}'

ONTASK_SCHEDULED_LOCKED_ITEM = '___ontask___scheduled___locked___item_{0}'

# Length of suffix to add to file names
ONTASK_SUFFIX_LENGTH = 512
