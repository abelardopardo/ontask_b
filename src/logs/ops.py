# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from .models import Log, log_types


def put(user, name, payload):

    if name not in log_types:
        raise Exception('Event', name, 'not allowed.')

    event = Log()
    event.user = user
    event.name = name
    event.payload = json.dumps(payload)
    event.save()
