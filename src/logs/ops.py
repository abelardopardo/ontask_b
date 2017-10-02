# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
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
    'action_create': 'Action created',
    'action_update': 'Action updated',
    'action_delete': 'Action deleted',
    'action_email_sent': 'Emails sent',
    'action_email_notify': 'Notification email sent',
    'action_served_execute': 'Action served',
    'condition_create': 'Condition created',
    'condition_update': 'Condition updated',
    'condition_delete': 'Condition deleted',
    'filter_create': 'Filter created',
    'filter_update': 'Filter updated',
    'filter_delete': 'Filter deleted',
}


def put(user, name, workflow, payload):

    if name not in log_types.keys():
        raise Exception('Event', name, 'not allowed.')

    event = Log()
    event.user = user
    event.name = name
    event.workflow = workflow
    event.payload = json.dumps(payload)
    event.save()
