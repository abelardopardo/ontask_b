# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .models import Log

log_types = {
    'workflow_create': 'Workflow created',
    'workflow_update': 'Workflow updated',
    'workflow_delete': 'Workflow deleted',
    'workflow_data_upload': 'Data uploaded to workflow',
    'workflow_data_merge': 'Data merged into workflow',
    'workflow_data_failedmerge': 'Failed data merge into workflow',
    'workflow_data_flush': 'Workflow data flushed',
    'workflow_attribute_create': 'New attribute in workflow',
    'workflow_attribute_update': 'Attributes updated in workflow',
    'workflow_attribute_delete': 'Attribute deleted',
    'workflow_share_add': 'User share added',
    'workflow_share_delete': 'User share deleted',
    'workflow_import': 'Import workflow',
    'workflow_clone': 'Workflow cloned',
    'column_add': 'Column added',
    'column_rename': 'Column renamed',
    'column_delete': 'Column deleted',
    'column_clone': 'Column cloned',
    'action_create': 'Action created',
    'action_update': 'Action updated',
    'action_delete': 'Action deleted',
    'action_clone': 'Action cloned',
    'action_email_sent': 'Emails sent',
    'action_email_notify': 'Notification email sent',
    'action_email_read': 'Email read',
    'action_serve_toggled': 'Action URL toggled',
    'action_served_execute': 'Action served',
    'condition_create': 'Condition created',
    'condition_update': 'Condition updated',
    'condition_delete': 'Condition deleted',
    'condition_clone': 'Condition cloned',
    'tablerow_update': 'Table row updated',
    'tablerow_create': 'Table row created',
    'view_create': 'Table view created',
    'view_edit': 'Table view edited',
    'view_delete': 'Table view deleted',
    'view_clone': 'Table view cloned',
    'filter_create': 'Filter created',
    'filter_update': 'Filter updated',
    'filter_delete': 'Filter deleted',
    'plugin_create': 'Plugin created',
    'plugin_update': 'Plugin updated',
    'plugin_delete': 'Plugin deleted',
    'plugin_execute': 'Plugin executed',
    'schedule_email_create': 'Created scheduled email action',
    'schedule_email_edit': 'Edit scheduled email action',
    'schedule_email_delete': 'Delete scheduled email action',
    'schedule_email_execute': 'Execute scheduled email action',
}


def put(user, name, workflow, payload):
    if name not in log_types.keys():
        raise Exception('Event', name, 'not allowed.')

    event = Log()
    event.user = user
    event.name = name
    event.workflow = workflow
    event.set_payload(payload)
    event.save()
