# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.utils.translation import ugettext_lazy as _

from .models import Log

log_types = {
    'workflow_create': _('Workflow created'),
    'workflow_update': _('Workflow updated'),
    'workflow_delete': _('Workflow deleted'),
    'workflow_data_upload': _('Data uploaded to workflow'),
    'workflow_data_merge': _('Data merged into workflow'),
    'workflow_data_failedmerge': _('Failed data merge into workflow'),
    'workflow_data_flush': _('Workflow data flushed'),
    'workflow_attribute_create': _('New attribute in workflow'),
    'workflow_attribute_update': _('Attributes updated in workflow'),
    'workflow_attribute_delete': _('Attribute deleted'),
    'workflow_share_add': _('User share added'),
    'workflow_share_delete': _('User share deleted'),
    'workflow_import': _('Import workflow'),
    'workflow_clone': _('Workflow cloned'),
    'column_add': _('Column added'),
    'column_rename': _('Column renamed'),
    'column_delete': _('Column deleted'),
    'column_clone': _('Column cloned'),
    'column_restrict': _('Column restricted'),
    'action_create': _('Action created'),
    'action_update': _('Action updated'),
    'action_delete': _('Action deleted'),
    'action_clone': _('Action cloned'),
    'action_email_sent': _('Emails sent'),
    'action_email_notify': _('Notification email sent'),
    'action_email_read': _('Email read'),
    'action_serve_toggled': _('Action URL toggled'),
    'action_served_execute': _('Action served'),
    'action_import': _('Action imported'),
    'condition_create': _('Condition created'),
    'condition_update': _('Condition updated'),
    'condition_delete': _('Condition deleted'),
    'condition_clone': _('Condition cloned'),
    'tablerow_update': _('Table row updated'),
    'tablerow_create': _('Table row created'),
    'view_create': _('Table view created'),
    'view_edit': _('Table view edited'),
    'view_delete': _('Table view deleted'),
    'view_clone': _('Table view cloned'),
    'filter_create': _('Filter created'),
    'filter_update': _('Filter updated'),
    'filter_delete': _('Filter deleted'),
    'plugin_create': _('Plugin created'),
    'plugin_update': _('Plugin updated'),
    'plugin_delete': _('Plugin deleted'),
    'plugin_execute': _('Plugin executed'),
    'sql_connection_create': _('SQL connection created'),
    'sql_connection_edit': _('SQL connection updated'),
    'sql_connection_delete': _('SQL connection deleted'),
    'sql_connection_clone': _('SQL connection cloned'),
    'schedule_email_create': _('Created scheduled email action'),
    'schedule_email_edit': _('Edit scheduled email action'),
    'schedule_email_delete': _('Delete scheduled email action'),
    'schedule_email_execute': _('Execute scheduled email action'),
}


def put(user, name, workflow, payload):
    if name not in log_types.keys():
        raise Exception(_('Event {0} not allowed.').format(name))

    event = Log()
    event.user = user
    event.name = name
    event.workflow = workflow
    event.set_payload(payload)
    event.save()

    return event
